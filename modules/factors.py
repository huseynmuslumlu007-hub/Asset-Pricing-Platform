import yfinance as yf
import numpy as np
import pandas as pd
import urllib.request
import io
import zipfile
import ssl


def get_ff_factors(period: str) -> pd.DataFrame:
    url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_daily_CSV.zip"
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
            zf = zipfile.ZipFile(io.BytesIO(r.read()))
            name = [n for n in zf.namelist() if n.endswith(".CSV") or n.endswith(".csv")][0]
            raw = zf.read(name).decode("utf-8")
    except Exception as e:
        raise ValueError(f"Could not download Fama-French factor data: {e}")

    lines = raw.split("\n")
    start = None
    for i, l in enumerate(lines):
        stripped = l.strip()
        if stripped and (stripped[:4].isdigit()):
            start = i
            break
    if start is None:
        raise ValueError("Could not parse Fama-French data file.")

    data_lines = []
    for l in lines[start:]:
        l = l.strip()
        if not l:
            break
        data_lines.append(l)

    rows = []
    for l in data_lines:
        parts = l.split(",")
        if len(parts) >= 6:
            try:
                date = pd.to_datetime(parts[0].strip(), format="%Y%m%d")
                vals = [float(x) / 100 for x in parts[1:6]]
                rows.append([date] + vals)
            except Exception:
                continue

    df = pd.DataFrame(rows, columns=["Date", "MKT_RF", "SMB", "HML", "RMW", "CMA"])
    df = df.set_index("Date").sort_index()
    return df


def run_factors(ticker: str, period: str) -> dict:

    stock = yf.download(ticker, period=period, auto_adjust=True, progress=False)
    if stock.empty:
        raise ValueError(f"No data for {ticker}")

    prices = stock["Close"].squeeze()
    ret = prices.pct_change().dropna()
    ret.index = pd.to_datetime(ret.index).tz_localize(None)
    ret.name = "stock"

    ff = get_ff_factors(period)

    combined = pd.DataFrame({"stock": ret}).join(ff, how="inner").dropna()
    if len(combined) < 60:
        raise ValueError("Not enough overlapping data to run factor regression.")

    y = combined["stock"].values - combined["MKT_RF"].values
    X_cols_3 = ["MKT_RF", "SMB", "HML"]
    X_cols_5 = ["MKT_RF", "SMB", "HML", "RMW", "CMA"]

    def ols(y, X_cols):
        X = combined[X_cols].values
        X = np.column_stack([np.ones(len(X)), X])
        try:
            betas = np.linalg.lstsq(X, y, rcond=None)[0]
            y_hat = X @ betas
            ss_res = np.sum((y - y_hat) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
            return betas, float(r2)
        except Exception:
            return np.zeros(len(X_cols) + 1), 0.0

    b3, r2_3 = ols(y, X_cols_3)
    b5, r2_5 = ols(y, X_cols_5)

    factor_means = {col: float(combined[col].mean() * 252) for col in X_cols_5}

    def contributions(betas, cols):
        return {cols[i]: round(float(betas[i + 1]) * factor_means.get(cols[i], 0), 6)
                for i in range(len(cols))}

    contrib_3 = contributions(b3, X_cols_3)
    contrib_5 = contributions(b5, X_cols_5)

    alpha_3 = float(b3[0] * 252)
    alpha_5 = float(b5[0] * 252)

    def profile(loadings: dict) -> str:
        tags = []
        if loadings.get("MKT_RF", 0) > 1.2:
            tags.append("high-beta")
        elif loadings.get("MKT_RF", 0) < 0.8:
            tags.append("defensive")
        if loadings.get("SMB", 0) > 0.3:
            tags.append("small-cap tilt")
        elif loadings.get("SMB", 0) < -0.3:
            tags.append("large-cap tilt")
        if loadings.get("HML", 0) > 0.3:
            tags.append("value")
        elif loadings.get("HML", 0) < -0.3:
            tags.append("growth")
        if loadings.get("RMW", 0) > 0.2:
            tags.append("high profitability")
        if loadings.get("CMA", 0) < -0.2:
            tags.append("aggressive investment")
        return ", ".join(tags) if tags else "diversified / no strong factor tilt"

    loadings_5 = {X_cols_5[i]: round(float(b5[i + 1]), 4) for i in range(len(X_cols_5))}
    factor_profile = profile(loadings_5)

    return {
        "ff3": {
            "alpha":         round(alpha_3, 6),
            "r2":            round(r2_3, 4),
            "loadings":      {X_cols_3[i]: round(float(b3[i + 1]), 4) for i in range(len(X_cols_3))},
            "contributions": contrib_3,
        },
        "ff5": {
            "alpha":         round(alpha_5, 6),
            "r2":            round(r2_5, 4),
            "loadings":      loadings_5,
            "contributions": contrib_5,
        },
        "factor_profile": factor_profile,
        "factor_means":   {k: round(v, 6) for k, v in factor_means.items()},
        "n_obs":          len(combined),
    }
