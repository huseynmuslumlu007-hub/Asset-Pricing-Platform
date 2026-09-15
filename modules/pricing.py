import yfinance as yf
import numpy as np
import pandas as pd


def run_pricing(ticker: str, period: str) -> dict:

    stock = yf.download(ticker, period=period, auto_adjust=True, progress=False)
    bench = yf.download("^GSPC", period=period, auto_adjust=True, progress=False)

    if stock.empty or bench.empty:
        raise ValueError(f"No price data found for {ticker}. Check the ticker symbol.")

    stock_close = stock["Close"].squeeze()
    bench_close = bench["Close"].squeeze()

    combined = pd.DataFrame({"stock": stock_close, "bench": bench_close}).dropna()
    if len(combined) < 30:
        raise ValueError("Not enough overlapping data. Try a longer period.")

    stock_prices = combined["stock"].values.astype(float)
    bench_prices = combined["bench"].values.astype(float)
    dates = combined.index.strftime("%Y-%m-%d").tolist()

    stock_ret = np.diff(stock_prices) / stock_prices[:-1]
    bench_ret = np.diff(bench_prices) / bench_prices[:-1]

    try:
        tnx = yf.download("^TNX", period="5d", progress=False)
        rf_ann = float(tnx["Close"].dropna().iloc[-1]) / 100
    except Exception:
        rf_ann = 0.043
    rf_daily = rf_ann / 252

    n = len(stock_ret)
    ann_stock = float(np.mean(stock_ret) * 252)
    ann_bench = float(np.mean(bench_ret) * 252)
    ann_vol   = float(np.std(stock_ret, ddof=1) * np.sqrt(252))

    cov       = np.cov(stock_ret, bench_ret)[0][1]
    var_bench = np.var(bench_ret, ddof=1)
    beta      = float(cov / var_bench)

    capm_exp  = rf_ann + beta * (ann_bench - rf_ann)
    alpha     = ann_stock - capm_exp

    excess    = stock_ret - rf_daily
    sharpe    = float(np.mean(excess) / np.std(excess, ddof=1) * np.sqrt(252))

    neg       = excess[excess < 0]
    down_dev  = float(np.sqrt(np.mean(neg ** 2)) * np.sqrt(252)) if len(neg) > 0 else 1e-9
    sortino   = float(np.mean(excess) * 252 / down_dev)

    treynor   = float((ann_stock - rf_ann) / beta) if beta != 0 else 0

    active    = stock_ret - bench_ret
    ir        = float(np.mean(active) / np.std(active, ddof=1) * np.sqrt(252))

    peak   = stock_prices[0]
    max_dd = 0.0
    for p in stock_prices:
        if p > peak:
            peak = p
        dd = (peak - p) / peak
        if dd > max_dd:
            max_dd = dd

    sorted_ret = np.sort(stock_ret)
    var95 = float(-sorted_ret[int(0.05 * n)])
    var99 = float(-sorted_ret[int(0.01 * n)])

    # Rolling beta — fixed: use integer index for dates
    window = 60
    roll_betas = []
    roll_dates = []
    for i in range(window, len(stock_ret) + 1):
        s = stock_ret[i - window:i]
        m = bench_ret[i - window:i]
        c = np.cov(s, m)[0][1]
        v = np.var(m, ddof=1)
        roll_betas.append(round(float(c / v), 4) if v != 0 else 0.0)
        roll_dates.append(dates[i])

    # Return distribution — fixed: use float bin edges not dates
    hist, bin_edges = np.histogram(stock_ret * 100, bins=30)
    dist_labels = [round(float(b), 3) for b in bin_edges[:-1]]
    dist_values = [int(v) for v in hist.tolist()]

    # Drawdown series
    peak = stock_prices[0]
    dd_series = []
    for p in stock_prices:
        if p > peak:
            peak = p
        dd_series.append(round(-((peak - p) / peak) * 100, 4))

    stock_rebased = (stock_prices / stock_prices[0] * 100).tolist()
    bench_rebased = (bench_prices / bench_prices[0] * 100).tolist()

    # SML — fixed: pure float betas, no datetime
    sml_betas   = [float(0), float(0.5), float(1.0), float(1.5), float(2.0), float(2.5)]
    sml_returns = [round(rf_ann + b * (ann_bench - rf_ann), 6) for b in sml_betas]

    return {
        "metrics": {
            "beta":         round(beta, 4),
            "ann_return":   round(ann_stock, 6),
            "bench_return": round(ann_bench, 6),
            "capm_exp":     round(capm_exp, 6),
            "alpha":        round(alpha, 6),
            "ann_vol":      round(ann_vol, 6),
            "sharpe":       round(sharpe, 4),
            "sortino":      round(sortino, 4),
            "treynor":      round(treynor, 4),
            "max_dd":       round(max_dd, 6),
            "var95":        round(var95, 6),
            "var99":        round(var99, 6),
            "ir":           round(ir, 4),
            "rf_ann":       round(rf_ann, 4),
            "n_days":       n,
        },
        "charts": {
            "dates":         dates,
            "stock_rebased": [round(float(v), 4) for v in stock_rebased],
            "bench_rebased": [round(float(v), 4) for v in bench_rebased],
            "roll_dates":    roll_dates,
            "roll_betas":    roll_betas,
            "dist_labels":   dist_labels,
            "dist_values":   dist_values,
            "dd_dates":      dates,
            "dd_series":     dd_series,
            "sml_betas":     sml_betas,
            "sml_returns":   sml_returns,
            "stock_beta":    round(beta, 4),
            "stock_return":  round(ann_stock, 6),
            "capm_return":   round(capm_exp, 6),
        }
    }
