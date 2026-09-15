import yfinance as yf
import numpy as np


def run_score(ticker: str, pricing: dict, factors: dict) -> dict:

    m = pricing["metrics"]
    f = factors["ff5"]

    scores = {}
    explanations = {}

    # ── 1. Risk-Adjusted Return Score (20%) ───────────────────────────
    sharpe = m["sharpe"]
    alpha = m["alpha"]

    if sharpe > 2.0:
        rar = 95
    elif sharpe > 1.5:
        rar = 85
    elif sharpe > 1.0:
        rar = 72
    elif sharpe > 0.5:
        rar = 55
    elif sharpe > 0:
        rar = 38
    else:
        rar = 15

    alpha_bonus = min(20, max(-20, alpha * 100))
    rar = min(100, max(0, rar + alpha_bonus * 0.3))
    scores["risk_adjusted"] = round(rar, 1)
    explanations["risk_adjusted"] = (
        f"Sharpe {sharpe:.2f} · Alpha {alpha*100:+.1f}%"
    )

    # ── 2. Momentum Score (20%) ────────────────────────────────────────
    try:
        hist = yf.download(ticker, period="1y", auto_adjust=True, progress=False)
        prices = hist["Close"].squeeze().dropna().values
        if len(prices) > 20:
            ret_12m = (prices[-1] - prices[0]) / prices[0]
            ret_3m  = (prices[-1] - prices[int(len(prices) * 0.75)]) / prices[int(len(prices) * 0.75)]
            ret_1m  = (prices[-1] - prices[int(len(prices) * 0.917)]) / prices[int(len(prices) * 0.917)]

            mom_score = 50
            mom_score += min(30, max(-30, ret_12m * 100))
            mom_score += min(15, max(-15, ret_3m * 100))
            mom_score += min(5,  max(-5,  ret_1m * 100))
            mom_score = min(100, max(0, mom_score))
        else:
            mom_score = 50
            ret_12m = ret_3m = ret_1m = 0
    except Exception:
        mom_score = 50
        ret_12m = ret_3m = ret_1m = 0

    scores["momentum"] = round(mom_score, 1)
    explanations["momentum"] = (
        f"12M {ret_12m*100:+.1f}% · 3M {ret_3m*100:+.1f}% · 1M {ret_1m*100:+.1f}%"
    )

    # ── 3. Quality Score (20%) ─────────────────────────────────────────
    try:
        info = yf.Ticker(ticker).info
        roe        = info.get("returnOnEquity", None)
        roic       = info.get("returnOnAssets", None)
        margins    = info.get("profitMargins", None)
        de_ratio   = info.get("debtToEquity", None)
        current_r  = info.get("currentRatio", None)

        quality = 50
        if roe is not None:
            quality += min(20, max(-10, roe * 100))
        if margins is not None:
            quality += min(15, max(-10, margins * 100))
        if de_ratio is not None:
            quality -= min(15, max(0, (de_ratio - 1) * 5))
        if current_r is not None:
            quality += min(10, max(-5, (current_r - 1) * 5))

        quality = min(100, max(0, quality))

        roe_str     = f"{roe*100:.1f}%" if roe else "N/A"
        margin_str  = f"{margins*100:.1f}%" if margins else "N/A"
        de_str      = f"{de_ratio:.2f}x" if de_ratio else "N/A"

    except Exception:
        quality = 50
        roe_str = margin_str = de_str = "N/A"

    scores["quality"] = round(quality, 1)
    explanations["quality"] = (
        f"ROE {roe_str} · Net margin {margin_str} · D/E {de_str}"
    )

    # ── 4. Valuation Score (25%) ───────────────────────────────────────
    try:
        info = yf.Ticker(ticker).info
        pe       = info.get("trailingPE", None)
        pb       = info.get("priceToBook", None)
        ps       = info.get("priceToSalesTrailing12Months", None)
        fwd_pe   = info.get("forwardPE", None)

        val = 50
        if pe is not None and pe > 0:
            if pe < 10:   val += 25
            elif pe < 15: val += 15
            elif pe < 20: val += 5
            elif pe < 30: val -= 5
            elif pe < 50: val -= 15
            else:         val -= 25

        if pb is not None and pb > 0:
            if pb < 1:    val += 10
            elif pb < 3:  val += 5
            elif pb < 5:  val -= 5
            else:         val -= 10

        if fwd_pe is not None and pe is not None and fwd_pe > 0 and pe > 0:
            if fwd_pe < pe:
                val += 5

        val = min(100, max(0, val))

        pe_str    = f"{pe:.1f}x"    if pe    else "N/A"
        pb_str    = f"{pb:.1f}x"    if pb    else "N/A"
        fwdpe_str = f"{fwd_pe:.1f}x" if fwd_pe else "N/A"

    except Exception:
        val = 50
        pe_str = pb_str = fwdpe_str = "N/A"

    scores["valuation"] = round(val, 1)
    explanations["valuation"] = (
        f"P/E {pe_str} · P/B {pb_str} · Fwd P/E {fwdpe_str}"
    )

    # ── 5. Factor Attractiveness Score (15%) ──────────────────────────
    loadings = f["loadings"]
    r2 = f["r2"]
    residual_alpha = f["alpha"]

    factor_score = 50
    factor_score += min(20, max(-20, residual_alpha * 100 * 2))
    factor_score += min(10, max(-10, (1 - r2) * 20))

    hmsl = loadings.get("HML", 0)
    rmw  = loadings.get("RMW", 0)
    if rmw > 0.2:
        factor_score += 10
    if hmsl > 0.2:
        factor_score += 5

    factor_score = min(100, max(0, factor_score))
    scores["factor"] = round(factor_score, 1)
    explanations["factor"] = (
        f"Residual α {residual_alpha*100:+.1f}% · R² {r2:.2f} · "
        f"RMW {loadings.get('RMW', 0):+.2f} · HML {loadings.get('HML', 0):+.2f}"
    )

    # ── Composite Score ────────────────────────────────────────────────
    weights = {
        "valuation":    0.25,
        "momentum":     0.20,
        "quality":      0.20,
        "risk_adjusted": 0.20,
        "factor":       0.15,
    }

    composite = sum(scores[k] * weights[k] for k in weights)
    composite = round(composite, 1)

    # ── Verdict ────────────────────────────────────────────────────────
    if composite >= 75:
        verdict = "Strong buy signal on a risk-adjusted, multi-factor basis."
        verdict_class = "positive"
    elif composite >= 60:
        verdict = "Attractive. Multiple signals positive — monitor valuation."
        verdict_class = "positive"
    elif composite >= 45:
        verdict = "Mixed signals. Some strengths offset by risk or valuation concerns."
        verdict_class = "neutral"
    elif composite >= 30:
        verdict = "Weak. Risk-adjusted returns and fundamentals disappoint."
        verdict_class = "negative"
    else:
        verdict = "Avoid. Most signals negative across valuation, momentum, and quality."
        verdict_class = "negative"

    return {
        "composite":   composite,
        "scores":      scores,
        "weights":     weights,
        "explanations": explanations,
        "verdict":     verdict,
        "verdict_class": verdict_class,
        "ticker":      ticker,
    }

    