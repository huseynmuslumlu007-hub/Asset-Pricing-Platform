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
        tnx = yf.download("^TNX", period="5d", progress=False, auto_adjust=True)
        rf_ann = float(tnx["Close"].squeeze().dropna().iloc[-1]) / 100
    except Exception:
        rf_ann = 0.05
    rf_daily = rf_ann / 252

    # ── Portfolio metrics ─────────────────────────────────────────────
    mean_ret = ret.mean().values
    cov_matrix = ret.cov().values

    port_ret_daily = float(weights @ mean_ret)
    # Geometric annualisation
    port_daily_series = ret.values @ weights
    n_port = len(port_daily_series)
    port_ann_ret = float((np.prod(1 + port_daily_series) ** (252 / n_port)) - 1)
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

    n_bench = len(aligned_bench)
    bench_ann = float((np.prod(1 + aligned_bench.values) ** (252 / n_bench)) - 1)
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
        ann_r = float((np.prod(1 + r) ** (252 / len(r))) - 1)
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

    ret_array = ret.values
    for _ in range(n_portfolios):
        w = np.random.dirichlet(np.ones(len(tickers)))
        port_ser = ret_array @ w
        r_ = float((np.prod(1 + port_ser) ** (252 / len(port_ser))) - 1)
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
        port_ser = ret.values @ w
        r_ = float((np.prod(1 + port_ser) ** (252 / len(port_ser))) - 1)
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



    

def score_portfolio(metrics: dict, holdings: list, min_var_weights: dict, max_sharpe_weights: dict, corr_matrix: dict) -> dict:
    scores = {}
    explanations = {}
    recommendations = []

    # Risk-Adjusted Return (25%)
    sharpe = metrics["sharpe"]
    if sharpe > 1.5:   rar = 90
    elif sharpe > 1.0: rar = 75
    elif sharpe > 0.7: rar = 60
    elif sharpe > 0.5: rar = 45
    elif sharpe > 0:   rar = 30
    else:              rar = 10
    scores["risk_adjusted"] = round(rar, 1)
    explanations["risk_adjusted"] = f"Sharpe {sharpe:.2f} vs market ~0.6 benchmark"

    # Alpha Generation (20%)
    alpha = metrics["alpha"]
    if alpha > 0.10:   alp = 90
    elif alpha > 0.05: alp = 75
    elif alpha > 0.02: alp = 60
    elif alpha > 0:    alp = 50
    elif alpha > -0.05: alp = 35
    else:              alp = 15
    scores["alpha"] = round(alp, 1)
    explanations["alpha"] = f"Portfolio alpha {alpha*100:+.2f}% above CAPM prediction"

    # Diversification (20%)
    labels = corr_matrix["labels"]
    values = corr_matrix["values"]
    n = len(labels)
    if n < 2:
        avg_corr = 1.0
    else:
        total, count = 0, 0
        for i in range(n):
            for j in range(n):
                if i != j:
                    total += abs(values[i][j])
                    count += 1
        avg_corr = total / count if count > 0 else 1.0

    if avg_corr < 0.3:   div = 95
    elif avg_corr < 0.5: div = 80
    elif avg_corr < 0.7: div = 60
    elif avg_corr < 0.85: div = 40
    else:                 div = 20
    scores["diversification"] = round(div, 1)
    explanations["diversification"] = f"Avg cross-asset correlation {avg_corr:.2f} — {'low' if avg_corr < 0.5 else 'high' if avg_corr > 0.7 else 'moderate'} diversification benefit"

    # Efficiency vs Max Sharpe (20%)
    current_weights = {h["ticker"]: h["weight"] for h in holdings}
    weight_diff = sum(abs(current_weights.get(t, 0) - max_sharpe_weights.get(t, 0)) for t in set(list(current_weights.keys()) + list(max_sharpe_weights.keys())))
    if weight_diff < 0.1:   eff = 95
    elif weight_diff < 0.3: eff = 75
    elif weight_diff < 0.5: eff = 55
    elif weight_diff < 0.7: eff = 35
    else:                   eff = 20
    scores["efficiency"] = round(eff, 1)
    explanations["efficiency"] = f"Current weights deviate {weight_diff*100:.0f}% from max-Sharpe optimal"

    # Drawdown Control (15%)
    mdd = metrics["max_dd"]
    if mdd < 0.10:   dd = 90
    elif mdd < 0.15: dd = 75
    elif mdd < 0.20: dd = 60
    elif mdd < 0.30: dd = 45
    elif mdd < 0.40: dd = 30
    else:            dd = 15
    scores["drawdown"] = round(dd, 1)
    explanations["drawdown"] = f"Max drawdown -{mdd*100:.1f}%"

    # Composite
    weights = {"risk_adjusted": 0.25, "alpha": 0.20, "diversification": 0.20, "efficiency": 0.20, "drawdown": 0.15}
    composite = round(sum(scores[k] * weights[k] for k in weights), 1)

    if composite >= 75:   verdict = "Strong portfolio. Risk-adjusted returns are compelling and construction is efficient."; vc = "positive"
    elif composite >= 60: verdict = "Solid portfolio with room to improve diversification or weight efficiency."; vc = "positive"
    elif composite >= 45: verdict = "Mixed signals. Good alpha but concentration or drawdown concerns drag the score."; vc = "neutral"
    elif composite >= 30: verdict = "Weak construction. Consider rebalancing toward optimised weights."; vc = "negative"
    else:                 verdict = "Poor risk-adjusted construction. High correlation and drawdown with limited alpha."; vc = "negative"

    # Weight recommendations
    for t in set(list(current_weights.keys()) + list(max_sharpe_weights.keys())):
        curr = current_weights.get(t, 0)
        opt  = max_sharpe_weights.get(t, 0)
        diff = opt - curr
        if abs(diff) > 0.03:
            direction = "Increase" if diff > 0 else "Reduce"
            recommendations.append({
                "ticker": t,
                "action": direction,
                "from": round(curr * 100, 1),
                "to": round(opt * 100, 1),
                "diff": round(diff * 100, 1)
            })
    recommendations.sort(key=lambda x: abs(x["diff"]), reverse=True)

    return {
        "composite": composite,
        "scores": scores,
        "weights": weights,
        "explanations": explanations,
        "verdict": verdict,
        "verdict_class": vc,
        "recommendations": recommendations,
        "avg_correlation": round(avg_corr, 3),
        "vs_max_sharpe_diff": round(weight_diff * 100, 1)
    }
