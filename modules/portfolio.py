import yfinance as yf
import numpy as np
import pandas as pd


def run_portfolio(tickers: list, weights: list, period: str) -> dict:

    # ── Fetch prices ──────────────────────────────────────────────────
    if not weights or len(weights) != len(tickers):
        weights = [1 / len(tickers)] * len(tickers)

    weights = np.array(weights, dtype=float)
    weights = weights / weights.sum()

    prices = {}
    for t in tickers:
        data = yf.download(t, period=period, auto_adjust=True, progress=False)
        if data.empty:
            raise ValueError(f"No data for {t}")
        prices[t] = data["Close"].squeeze()

    df = pd.DataFrame(prices).dropna()
    if len(df) < 30:
        raise ValueError("Not enough overlapping data across all tickers.")

    # ── Returns ───────────────────────────────────────────────────────
    ret = df.pct_change().dropna()
    n = len(ret)

    # ── Benchmark ────────────────────────────────────────────────────
    bench = yf.download("^GSPC", period=period, auto_adjust=True, progress=False)
    bench_close = bench["Close"].squeeze().reindex(df.index).dropna()
    bench_ret = bench_close.pct_change().dropna()

    # ── Risk-free rate ────────────────────────────────────────────────
    try:
        tnx = yf.download("^TNX", period="5d", progress=False)
        rf_ann = float(tnx["Close"].dropna().iloc[-1]) / 100
    except Exception:
        rf_ann = 0.043
    rf_daily = rf_ann / 252

    # ── Portfolio metrics ─────────────────────────────────────────────
    mean_ret = ret.mean().values
    cov_matrix = ret.cov().values

    port_ret_daily = float(weights @ mean_ret)
    port_ann_ret = port_ret_daily * 252
    port_ann_vol = float(np.sqrt(weights @ cov_matrix @ weights) * np.sqrt(252))
    port_sharpe = (port_ann_ret - rf_ann) / port_ann_vol if port_ann_vol > 0 else 0

    # Portfolio daily returns series
    port_daily = ret.values @ weights
    neg = port_daily[port_daily < 0] - rf_daily
    down_dev = float(np.sqrt(np.mean(neg ** 2)) * np.sqrt(252)) if len(neg) > 0 else 1e-9
    port_sortino = float((port_ann_ret - rf_ann) / down_dev)

    # Beta vs benchmark
    aligned_bench = bench_ret.reindex(ret.index).dropna()
    aligned_port = pd.Series(port_daily, index=ret.index).reindex(aligned_bench.index).dropna()
    cov_pb = float(np.cov(aligned_port.values, aligned_bench.values)[0][1])
    var_b = float(np.var(aligned_bench.values, ddof=1))
    port_beta = cov_pb / var_b if var_b > 0 else 1.0

    bench_ann = float(aligned_bench.mean() * 252)
    port_capm = rf_ann + port_beta * (bench_ann - rf_ann)
    port_alpha = port_ann_ret - port_capm

    # Max drawdown
    port_prices = (1 + pd.Series(port_daily)).cumprod().values
    peak = port_prices[0]
    max_dd = 0.0
    for p in port_prices:
        if p > peak:
            peak = p
        dd = (peak - p) / peak
        if dd > max_dd:
            max_dd = dd

    # VaR
    sorted_ret = np.sort(port_daily)
    var95 = float(-sorted_ret[int(0.05 * n)])
    var99 = float(-sorted_ret[int(0.01 * n)])

    # ── Correlation matrix ────────────────────────────────────────────
    corr = ret.corr()
    corr_matrix = {
        "labels": tickers,
        "values": [[round(float(corr.loc[t1, t2]), 4) for t2 in tickers] for t1 in tickers]
    }

    # ── Individual stock metrics ──────────────────────────────────────
    holdings = []
    for i, t in enumerate(tickers):
        r = ret[t].values
        ann_r = float(np.mean(r) * 252)
        ann_v = float(np.std(r, ddof=1) * np.sqrt(252))
        exc = r - rf_daily
        sh = float(np.mean(exc) / np.std(exc, ddof=1) * np.sqrt(252)) if np.std(exc) > 0 else 0
        holdings.append({
            "ticker": t,
            "weight": round(float(weights[i]), 4),
            "ann_return": round(ann_r, 4),
            "ann_vol": round(ann_v, 4),
            "sharpe": round(sh, 4),
        })

    # ── Efficient frontier (Monte Carlo) ──────────────────────────────
    np.random.seed(42)
    n_portfolios = 3000
    ef_returns, ef_vols, ef_sharpes = [], [], []

    for _ in range(n_portfolios):
        w = np.random.dirichlet(np.ones(len(tickers)))
        r_ = float(w @ mean_ret * 252)
        v_ = float(np.sqrt(w @ cov_matrix @ w) * np.sqrt(252))
        s_ = (r_ - rf_ann) / v_ if v_ > 0 else 0
        ef_returns.append(round(r_, 6))
        ef_vols.append(round(v_, 6))
        ef_sharpes.append(round(s_, 4))

    # Min variance portfolio
    from scipy.optimize import minimize

    def port_vol(w):
        return float(np.sqrt(w @ cov_matrix @ w) * np.sqrt(252))

    def neg_sharpe(w):
        r_ = float(w @ mean_ret * 252)
        v_ = port_vol(w)
        return -(r_ - rf_ann) / v_ if v_ > 0 else 0

    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]
    bounds = [(0, 1)] * len(tickers)
    w0 = np.ones(len(tickers)) / len(tickers)

    min_var = minimize(port_vol, w0, method="SLSQP", bounds=bounds, constraints=constraints)
    max_sh = minimize(neg_sharpe, w0, method="SLSQP", bounds=bounds, constraints=constraints)

    def fmt_weights(w):
        return {tickers[i]: round(float(w[i]), 4) for i in range(len(tickers))}

    # ── Cumulative performance chart ──────────────────────────────────
    dates = df.index.strftime("%Y-%m-%d").tolist()[1:]
    port_cumulative = (port_prices / port_prices[0] * 100).tolist()

    bench_prices_aligned = bench_close.reindex(df.index).ffill().values
    bench_cumulative = (bench_prices_aligned / bench_prices_aligned[0] * 100).tolist()

    return {
        "metrics": {
            "ann_return":  round(port_ann_ret, 6),
            "ann_vol":     round(port_ann_vol, 6),
            "sharpe":      round(port_sharpe, 4),
            "sortino":     round(port_sortino, 4),
            "beta":        round(port_beta, 4),
            "alpha":       round(port_alpha, 6),
            "max_dd":      round(max_dd, 6),
            "var95":       round(var95, 6),
            "var99":       round(var99, 6),
            "rf_ann":      round(rf_ann, 4),
            "n_assets":    len(tickers),
        },
        "holdings":     holdings,
        "corr_matrix":  corr_matrix,
        "efficient_frontier": {
            "returns":  ef_returns,
            "vols":     ef_vols,
            "sharpes":  ef_sharpes,
        },
        "min_var_weights":  fmt_weights(min_var.x),
        "max_sharpe_weights": fmt_weights(max_sh.x),
        "charts": {
            "dates":             dates,
            "port_cumulative":   [round(v, 4) for v in port_cumulative],
            "bench_cumulative":  [round(v, 4) for v in bench_cumulative],
        }
    }



    