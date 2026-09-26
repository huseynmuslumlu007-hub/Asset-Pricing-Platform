content = open('templates/index.html').read()

old = """// ─────────────────────────────────────────────
//  Metric explanation modals
// ─────────────────────────────────────────────
function explainMetric(key, ticker, m) {"""

new = """// ─────────────────────────────────────────────
//  Metric explanation modals — two-panel
// ─────────────────────────────────────────────
function metricLeftHTML(label, value, color, sub, badge) {
  return `
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:260px;text-align:center;gap:12px">
      <div style="font-size:11px;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:1px">${label}</div>
      <div style="font-family:var(--mono);font-size:64px;font-weight:700;letter-spacing:-2px;color:${color};line-height:1">${value}</div>
      ${sub ? `<div style="font-size:13px;color:var(--muted)">${sub}</div>` : ''}
      ${badge ? `<span style="background:rgba(209,213,219,0.1);border:1px solid rgba(209,213,219,0.2);border-radius:20px;padding:4px 14px;font-size:11px;font-weight:700;color:var(--accent)">${badge}</span>` : ''}
    </div>`;
}

function explainMetric(key, ticker, m) {"""

if old in content:
    content = content.replace(old, new)
    print('explainMetric header: OK')
else:
    print('explainMetric header: ERROR')

# Now replace the entire explainMetric function body to use new modal
old2 = """  const defs = {
    beta: {
      title: 'Beta — Systematic Risk', sub: 'How sensitive this stock is to overall market movements',
      cards: [
        { label: 'What it measures', value: fix3(m.beta), color: m.beta > 1.2 ? '#ef4444' : m.beta < 0.8 ? '#22c55e' : '#d1d5db',
          text: `${ticker}'s beta of ${fix3(m.beta)} means when the S&P 500 moves 1%, ${ticker} typically moves ${(m.beta*100).toFixed(1)}%. Values above 1 amplify market moves; below 1 dampens them.` },
        { label: 'Interpretation', value: m.beta > 1.2 ? 'High Beta' : m.beta < 0.8 ? 'Defensive' : 'Market-like', color: '#d1d5db',
          text: m.beta > 1.2 ? `${ticker} is more volatile than the market. In bull markets it outperforms; in downturns it falls harder.` : m.beta < 0.8 ? `${ticker} is more stable than the market — it moves less when markets swing. Typical of defensive sectors.` : `${ticker} moves roughly in line with the broader market.` },
        { label: 'Methodology note', value: '1Y daily returns', color: '#718096',
          text: `This beta uses 1-year daily return data. Bloomberg and Google typically show 5-year monthly beta, which will differ. Ours reflects recent sensitivity more accurately.` },
        { label: 'Context', value: `vs RF ${pct(m.rf_ann)}`, color: '#718096',
          text: `With a risk-free rate of ${pct(m.rf_ann)}, the market risk premium (ERP) used in CAPM is approximately ${pct(m.bench_return - m.rf_ann)}. Beta scales this premium.` }
      ]
    },
    return: {
      title: 'Realised Return — Actual Performance', sub: 'What the stock actually returned over the selected period',
      cards: [
        { label: 'Stock return', value: pct(m.ann_return), color: m.ann_return >= 0 ? '#22c55e' : '#ef4444',
          text: `${ticker} delivered ${pct(m.ann_return)} annualised over this period. This is the geometric annualised return — correctly accounts for compounding.` },
        { label: 'Market return', value: pct(m.bench_return), color: '#d1d5db',
          text: `The S&P 500 returned ${pct(m.bench_return)} over the same period. This is your benchmark for comparison.` },
        { label: 'Outperformance', value: pct(m.ann_return - m.bench_return), color: (m.ann_return - m.bench_return) >= 0 ? '#22c55e' : '#ef4444',
          text: `${ticker} ${m.ann_return > m.bench_return ? 'beat' : 'trailed'} the market by ${Math.abs((m.ann_return - m.bench_return)*100).toFixed(2)}% per year. Note this is raw outperformance — it doesn't account for the risk taken to achieve it.` },
        { label: 'Risk-adjusted view', value: `Sharpe ${fix2(m.sharpe)}`, color: '#d1d5db',
          text: `Raw return alone is incomplete. ${ticker}'s Sharpe of ${fix2(m.sharpe)} tells you how much return you got per unit of risk — a more complete picture.` }
      ]
    },
    capm: {
      title: 'CAPM Expected Return — Theoretical Benchmark', sub: 'What return the market theoretically demands for this level of risk',
      cards: [
        { label: 'CAPM formula', value: pct(m.capm_exp), color: '#d1d5db',
          text: `CAPM Expected = Rf + β × (Rm − Rf) = ${pct(m.rf_ann)} + ${fix3(m.beta)} × ${pct(m.bench_return - m.rf_ann)} = ${pct(m.capm_exp)}` },
        { label: 'Risk-free rate', value: pct(m.rf_ann), color: '#718096',
          text: `The current 10-Year US Treasury yield of ${pct(m.rf_ann)} is used as the risk-free rate — the return you get for taking zero risk.` },
        { label: 'Equity risk premium', value: pct(m.bench_return - m.rf_ann), color: '#d1d5db',
          text: `The market excess return (ERP) is ${pct(m.bench_return - m.rf_ann)}. Beta of ${fix3(m.beta)} scales this: higher beta = higher required return.` },
        { label: 'What it means', value: `Required ${pct(m.capm_exp)}`, color: '#d1d5db',
          text: `Investors should demand at least ${pct(m.capm_exp)} from ${ticker} to be compensated for its systematic risk. Whether it delivers more or less is Jensen's Alpha.` }
      ]
    },
    alpha: {
      title: "Jensen's Alpha — Genuine Outperformance", sub: 'Return above what CAPM predicts for this level of risk',
      cards: [
        { label: "Jensen's Alpha", value: pct(m.alpha), color: m.alpha >= 0 ? '#22c55e' : '#ef4444',
          text: `Alpha = Realised Return − CAPM Expected = ${pct(m.ann_return)} − ${pct(m.capm_exp)} = ${pct(m.alpha)}. This is the return ${ticker} delivered above what its risk level justified.` },
        { label: 'Significance', value: m.alpha > 0 ? 'Positive Alpha' : 'Negative Alpha', color: m.alpha >= 0 ? '#22c55e' : '#ef4444',
          text: m.alpha > 0 ? `${ticker} is generating genuine excess return beyond what its systematic risk alone would predict. This is what PMs hunt for.` : `${ticker} is underperforming its theoretical required return. You're taking this much risk but not being adequately compensated.` },
        { label: 'vs Factor alpha', value: 'See Factor Analysis', color: '#718096',
          text: `CAPM alpha only adjusts for market risk. The Factor Analysis module shows residual alpha after controlling for size, value, profitability and momentum factors — a more rigorous measure.` },
        { label: 'Practical note', value: 'Use with IR', color: '#718096',
          text: `Alpha tells you magnitude but not consistency. Pair it with the Information Ratio (${fix2(m.ir)}) to understand whether this alpha is persistent or luck.` }
      ]
    },
    sharpe: {
      title: 'Sharpe Ratio — Risk-Adjusted Return', sub: 'How much return you earned per unit of total risk taken',
      cards: [
        { label: 'Sharpe Ratio', value: fix2(m.sharpe), color: m.sharpe > 1 ? '#22c55e' : m.sharpe > 0.5 ? '#f59e0b' : '#ef4444',
          text: `Sharpe = (Return − Rf) / Volatility = (${pct(m.ann_return)} − ${pct(m.rf_ann)}) / ${pct(m.ann_vol)} = ${fix2(m.sharpe)}` },
        { label: 'Benchmark', value: '> 1.0 = Good', color: '#d1d5db',
          text: `A Sharpe above 1.0 is generally considered good. Above 2.0 is exceptional. Below 0.5 suggests poor risk-adjusted returns. ${ticker} at ${fix2(m.sharpe)} is ${m.sharpe > 1 ? 'above' : 'below'} the threshold.` },
        { label: 'Limitation', value: 'Penalises upside', color: '#718096',
          text: `Sharpe penalises all volatility — including positive surprises. If ${ticker} has a lot of upside volatility, the Sortino Ratio (${fix2(m.sortino)}) is more appropriate.` },
        { label: 'vs Market', value: `Market ~0.5–0.7`, color: '#718096',
          text: `A well-diversified market portfolio typically has a Sharpe of 0.5–0.7 over long periods. ${ticker}'s ${fix2(m.sharpe)} ${m.sharpe > 0.7 ? 'exceeds' : 'is below'} this baseline.` }
      ]
    },
    sortino: {
      title: 'Sortino Ratio — Downside Risk-Adjusted Return', sub: 'Like Sharpe but only penalises harmful downside volatility',
      cards: [
        { label: 'Sortino Ratio', value: fix2(m.sortino), color: m.sortino > 1 ? '#22c55e' : m.sortino > 0.5 ? '#f59e0b' : '#ef4444',
          text: `Sortino = (Return − Rf) / Downside Deviation = ${fix2(m.sortino)}. Only negative return days count toward the denominator.` },
        { label: 'vs Sharpe', value: `Sharpe ${fix2(m.sharpe)}`, color: '#d1d5db',
          text: `${ticker}'s Sortino (${fix2(m.sortino)}) is ${m.sortino > m.sharpe ? 'higher' : 'lower'} than its Sharpe (${fix2(m.sharpe)}). ${m.sortino > m.sharpe ? 'This means upside volatility is larger than downside — a good sign.' : 'Downside moves dominate total volatility.'}` },
        { label: 'Practical use', value: 'Downside focus', color: '#718096',
          text: `For investors who care more about avoiding losses than capturing all gains, Sortino is the more relevant ratio. Pension funds and risk-averse mandates typically use it.` }
      ]
    },
    treynor: {
      title: 'Treynor Ratio — Systematic Risk-Adjusted Return', sub: 'Return per unit of market (systematic) risk specifically',
      cards: [
        { label: 'Treynor Ratio', value: fix2(m.treynor), color: m.treynor > 0 ? '#22c55e' : '#ef4444',
          text: `Treynor = (Return − Rf) / Beta = (${pct(m.ann_return)} − ${pct(m.rf_ann)}) / ${fix3(m.beta)} = ${fix2(m.treynor)}` },
        { label: 'When to use it', value: 'Portfolio context', color: '#d1d5db',
          text: `Treynor is most useful when comparing stocks within a diversified portfolio, where idiosyncratic risk is already diversified away. Only systematic risk (beta) matters at the portfolio level.` },
        { label: 'vs Sharpe', value: 'Different risk base', color: '#718096',
          text: `Sharpe uses total volatility; Treynor uses beta. If ${ticker} has high idiosyncratic risk, Treynor will look better than Sharpe. Use Sharpe for standalone analysis, Treynor for portfolio additions.` }
      ]
    },
    vol: {
      title: 'Volatility — Total Price Risk', sub: 'How much the stock price fluctuates on an annualised basis',
      cards: [
        { label: 'Annualised volatility', value: pct(m.ann_vol), color: m.ann_vol > 0.35 ? '#ef4444' : m.ann_vol > 0.2 ? '#f59e0b' : '#22c55e',
          text: `${ticker}'s price fluctuates by approximately ±${(m.ann_vol*100).toFixed(1)}% per year (1 standard deviation). This means in a typical year, returns could range from ${pct(m.ann_return - m.ann_vol)} to ${pct(m.ann_return + m.ann_vol)}.` },
        { label: 'Market comparison', value: 'S&P ~15–18%', color: '#d1d5db',
          text: `The S&P 500 typically has 15–18% annualised volatility. ${ticker} at ${pct(m.ann_vol)} is ${m.ann_vol > 0.18 ? 'more volatile' : 'less volatile'} than the broad market.` },
        { label: 'Daily equivalent', value: `±${(m.ann_vol/Math.sqrt(252)*100).toFixed(2)}% per day`, color: '#718096',
          text: `Daily volatility is ${(m.ann_vol/Math.sqrt(252)*100).toFixed(2)}%. On a typical trading day, ${ticker} moves this much in either direction.` }
      ]
    },
    drawdown: {
      title: 'Maximum Drawdown — Worst Historical Loss', sub: 'The largest peak-to-trough decline in the analysis period',
      cards: [
        { label: 'Max Drawdown', value: `-${(m.max_dd*100).toFixed(2)}%`, color: '#ef4444',
          text: `At some point in this period, ${ticker} fell ${(m.max_dd*100).toFixed(2)}% from its peak before recovering. This is the single worst loss an investor would have experienced if they bought at the top.` },
        { label: 'Recovery context', value: 'See DD chart', color: '#d1d5db',
          text: `The drawdown chart shows every down period over time. How quickly the stock recovered after hitting -${(m.max_dd*100).toFixed(2)}% tells you about its resilience.` },
        { label: 'Risk framing', value: `${(m.max_dd*100).toFixed(0)}% loss scenario`, color: '#718096',
          text: `A ${(m.max_dd*100).toFixed(0)}% drawdown on a $100,000 position would mean a paper loss of $${(m.max_dd*100000).toLocaleString()}. This helps frame downside risk in real terms.` }
      ]
    },
    var95: {
      title: 'Value at Risk 95% — Daily Tail Risk', sub: 'The daily loss threshold exceeded only 5% of trading days',
      cards: [
        { label: 'VaR 95%', value: `-${(m.var95*100).toFixed(2)}%`, color: '#ef4444',
          text: `On 95% of trading days, ${ticker} does not lose more than ${(m.var95*100).toFixed(2)}% in a single day. On the remaining 5% — about 13 days per year — losses can be worse.` },
        { label: 'Methodology', value: 'Historical simulation', color: '#d1d5db',
          text: `This uses the 5th percentile of actual historical daily returns. No distributional assumption — it reads directly from what the stock has actually done.` },
        { label: 'Dollar framing', value: `$${(m.var95*10000).toFixed(0)} per $10K`, color: '#718096',
          text: `On a $10,000 position, a VaR 95% event means losing up to $${(m.var95*10000).toFixed(0)} in a single bad day.` }
      ]
    },
    var99: {
      title: 'Value at Risk 99% — Extreme Tail Risk', sub: 'The daily loss threshold exceeded only 1% of trading days',
      cards: [
        { label: 'VaR 99%', value: `-${(m.var99*100).toFixed(2)}%`, color: '#ef4444',
          text: `Only 1% of trading days — about 2–3 days per year — produce losses worse than ${(m.var99*100).toFixed(2)}%. This captures rare but severe market events.` },
        { label: 'vs VaR 95%', value: `Gap: ${((m.var99-m.var95)*100).toFixed(2)}%`, color: '#d1d5db',
          text: `The gap between VaR 99% and VaR 95% is ${((m.var99-m.var95)*100).toFixed(2)}%. A large gap indicates fat tails — extreme moves are much worse than typical bad days.` },
        { label: 'Limitation', value: 'Not worst-case', color: '#718096',
          text: `VaR 99% does NOT tell you the worst possible loss — only the threshold. Losses in the 1% tail can be far larger.` }
      ]
    },
    ir: {
      title: 'Information Ratio — Alpha Consistency', sub: 'How consistently the stock outperforms its benchmark',
      cards: [
        { label: 'Information Ratio', value: fix2(m.ir), color: m.ir > 0.5 ? '#22c55e' : m.ir > 0 ? '#f59e0b' : '#ef4444',
          text: `IR = Active Return / Tracking Error = ${fix2(m.ir)}. Active return is ${ticker}'s average daily excess return over the S&P 500; tracking error is the volatility of those excess returns.` },
        { label: 'Benchmark', value: '> 0.5 = Good', color: '#d1d5db',
          text: `An IR above 0.5 is considered good; above 1.0 is exceptional. ${ticker} at ${fix2(m.ir)} is ${m.ir > 0.5 ? 'comfortably above' : m.ir > 0 ? 'below' : 'well below'} the threshold.` },
        { label: 'Alpha persistence', value: `Alpha ${pct(m.alpha)}`, color: '#718096',
          text: `Alpha (${pct(m.alpha)}) tells you the magnitude of outperformance. IR tells you how reliably it happens. High alpha with low IR means lumpy, unpredictable outperformance.` }
      ]
    }
  };
  const d = defs[key];
  if (d) openModal(d.title, d.sub, d.cards);
}"""

new2 = """  const metricColors = {
    beta: m.beta > 1.2 ? '#ef4444' : m.beta < 0.8 ? '#22c55e' : '#d1d5db',
    return: m.ann_return >= 0 ? '#22c55e' : '#ef4444',
    capm: '#d1d5db', alpha: m.alpha >= 0 ? '#22c55e' : '#ef4444',
    sharpe: m.sharpe > 1 ? '#22c55e' : m.sharpe > 0.5 ? '#f59e0b' : '#ef4444',
    sortino: m.sortino > 1 ? '#22c55e' : m.sortino > 0.5 ? '#f59e0b' : '#ef4444',
    treynor: m.treynor > 0 ? '#22c55e' : '#ef4444',
    vol: m.ann_vol > 0.35 ? '#ef4444' : m.ann_vol > 0.2 ? '#f59e0b' : '#22c55e',
    drawdown: '#ef4444', var95: '#ef4444', var99: '#ef4444',
    ir: m.ir > 0.5 ? '#22c55e' : m.ir > 0 ? '#f59e0b' : '#ef4444'
  };
  const metricValues = {
    beta: fix3(m.beta), return: pct(m.ann_return), capm: pct(m.capm_exp),
    alpha: pct(m.alpha), sharpe: fix2(m.sharpe), sortino: fix2(m.sortino),
    treynor: fix2(m.treynor), vol: pct(m.ann_vol),
    drawdown: '-' + (m.max_dd*100).toFixed(2) + '%',
    var95: '-' + (m.var95*100).toFixed(2) + '%',
    var99: '-' + (m.var99*100).toFixed(2) + '%',
    ir: fix2(m.ir)
  };
  const metricSubs = {
    beta: `Market: ${pct(m.bench_return)} · RF: ${pct(m.rf_ann)}`,
    return: `Market: ${pct(m.bench_return)}`,
    capm: `RF ${pct(m.rf_ann)} + β${fix3(m.beta)} × ERP`,
    alpha: `Realised ${pct(m.ann_return)} − CAPM ${pct(m.capm_exp)}`,
    sharpe: `(${pct(m.ann_return)} − ${pct(m.rf_ann)}) ÷ ${pct(m.ann_vol)}`,
    sortino: `Sharpe: ${fix2(m.sharpe)}`,
    treynor: `Beta: ${fix3(m.beta)}`,
    vol: `Daily: ±${(m.ann_vol/Math.sqrt(252)*100).toFixed(2)}%`,
    drawdown: `$${(m.max_dd*100000).toLocaleString()} loss per $100K`,
    var95: `~13 bad days per year`,
    var99: `~2-3 extreme days per year`,
    ir: `Alpha: ${pct(m.alpha)}`
  };

  const leftHTML = metricLeftHTML(
    key.toUpperCase().replace('_',' '),
    metricValues[key] || '',
    metricColors[key] || '#d1d5db',
    metricSubs[key] || '',
    ''
  );

  const cardDefs = {
    beta: [
      { label: 'What beta means', value: fix3(m.beta), color: metricColors.beta,
        text: `${ticker}'s beta of ${fix3(m.beta)} means when the S&P 500 moves 1%, ${ticker} typically moves ${(m.beta*100).toFixed(1)}%. Values above 1 amplify market moves; below 1 dampens them.` },
      { label: m.beta > 1.2 ? 'High beta risk' : m.beta < 0.8 ? 'Defensive profile' : 'Market-like', value: m.beta > 1.2 ? 'Aggressive' : m.beta < 0.8 ? 'Defensive' : 'Neutral', color: metricColors.beta,
        text: m.beta > 1.2 ? `${ticker} amplifies market moves. Expect bigger gains in bull markets and bigger losses in selloffs.` : m.beta < 0.8 ? `${ticker} cushions market moves. It will lag in rallies but hold up better in downturns.` : `${ticker} moves broadly in line with the S&P 500.` },
      { label: 'Methodology note', value: '1Y daily returns', color: '#718096',
        text: `Our beta uses 1-year daily returns. Google and Bloomberg show 5-year monthly beta — that is why their figure differs. Ours is more recent and more sensitive to current market regime.` },
      { label: 'CAPM implication', value: `Required ${pct(m.capm_exp)}`, color: '#718096',
        text: `A beta of ${fix3(m.beta)} with a market risk premium of ${pct(m.bench_return - m.rf_ann)} means CAPM requires ${pct(m.capm_exp)} return from ${ticker}.` }
    ],
    return: [
      { label: `${ticker} annualised return`, value: pct(m.ann_return), color: metricColors.return,
        text: `${ticker} delivered ${pct(m.ann_return)} per year over this period. This is geometric annualisation — it correctly compounds daily returns, unlike simple arithmetic averaging.` },
      { label: 'vs S&P 500', value: pct(m.bench_return), color: '#d1d5db',
        text: `The S&P 500 returned ${pct(m.bench_return)} over the same period. ${ticker} ${m.ann_return > m.bench_return ? 'beat' : 'trailed'} it by ${Math.abs((m.ann_return-m.bench_return)*100).toFixed(2)}% per year.` },
      { label: 'Outperformance', value: pct(m.ann_return - m.bench_return), color: (m.ann_return-m.bench_return) >= 0 ? '#22c55e' : '#ef4444',
        text: `Raw outperformance of ${pct(m.ann_return-m.bench_return)} per year. This does not account for risk — a stock can beat the market by taking far more risk. See alpha and Sharpe for the risk-adjusted picture.` },
      { label: 'Risk-adjusted view', value: `Sharpe ${fix2(m.sharpe)}`, color: '#d1d5db',
        text: `${ticker}'s Sharpe of ${fix2(m.sharpe)} tells you how much return you got per unit of risk taken. A stock with a lower return but higher Sharpe is often the better investment.` }
    ],
    capm: [
      { label: 'CAPM formula result', value: pct(m.capm_exp), color: '#d1d5db',
        text: `CAPM Expected = RF + β × (Rm − RF) = ${pct(m.rf_ann)} + ${fix3(m.beta)} × ${pct(m.bench_return-m.rf_ann)} = ${pct(m.capm_exp)}` },
      { label: 'Risk-free rate', value: pct(m.rf_ann), color: '#718096',
        text: `The 10-Year US Treasury yield of ${pct(m.rf_ann)} is the risk-free rate — what you earn for taking zero risk. Every risky asset must beat this to be worth holding.` },
      { label: 'Market risk premium', value: pct(m.bench_return - m.rf_ann), color: '#d1d5db',
        text: `The market earned ${pct(m.bench_return)} vs a risk-free rate of ${pct(m.rf_ann)}, giving an ERP of ${pct(m.bench_return-m.rf_ann)}. Beta of ${fix3(m.beta)} scales this: ${ticker} must earn ${pct(m.beta*(m.bench_return-m.rf_ann))} of market premium.` },
      { label: 'The verdict', value: `Actual: ${pct(m.ann_return)}`, color: m.ann_return >= m.capm_exp ? '#22c55e' : '#ef4444',
        text: `${ticker} ${m.ann_return >= m.capm_exp ? 'exceeded' : 'fell short of'} its CAPM requirement of ${pct(m.capm_exp)} by ${pct(Math.abs(m.alpha))}. This gap is Jensen's Alpha.` }
    ],
    alpha: [
      { label: "Jensen's Alpha", value: pct(m.alpha), color: metricColors.alpha,
        text: `Alpha = ${pct(m.ann_return)} − ${pct(m.capm_exp)} = ${pct(m.alpha)}. ${ticker} returned ${pct(Math.abs(m.alpha))} ${m.alpha >= 0 ? 'more than' : 'less than'} what its risk level theoretically required.` },
      { label: m.alpha >= 0 ? 'Genuine outperformance' : 'Underperformance', value: m.alpha >= 0 ? 'Positive alpha' : 'Negative alpha', color: metricColors.alpha,
        text: m.alpha >= 0 ? `${ticker} is generating real excess return that cannot be explained by systematic risk alone. This is exactly what active managers and stock pickers are looking for.` : `${ticker} is not compensating for the risk it carries. You could achieve a similar risk-adjusted return with a simpler index allocation.` },
      { label: 'Consistency check', value: `IR ${fix2(m.ir)}`, color: '#718096',
        text: `An alpha of ${pct(m.alpha)} with an IR of ${fix2(m.ir)} means this outperformance is ${m.ir > 0.5 ? 'consistent and reliable' : 'inconsistent — it may be partly luck'}.` },
      { label: 'Stricter test', value: 'See Factor Analysis', color: '#718096',
        text: `CAPM alpha only strips out market risk. Factor Analysis strips out five risk factors. If alpha survives the FF5 test, it is genuinely stock-specific.` }
    ],
    sharpe: [
      { label: 'Sharpe Ratio', value: fix2(m.sharpe), color: metricColors.sharpe,
        text: `Sharpe = (${pct(m.ann_return)} − ${pct(m.rf_ann)}) ÷ ${pct(m.ann_vol)} = ${fix2(m.sharpe)}. For every 1% of risk (volatility) taken, ${ticker} delivered ${fix2(m.sharpe)}% of excess return.` },
      { label: 'Interpretation', value: m.sharpe > 1 ? 'Strong' : m.sharpe > 0.5 ? 'Adequate' : 'Weak', color: metricColors.sharpe,
        text: `Above 1.0 is considered good. The broad market typically achieves 0.5–0.7 over long periods. ${ticker} at ${fix2(m.sharpe)} is ${m.sharpe > 1 ? 'well above' : m.sharpe > 0.7 ? 'above' : 'below'} the market baseline.` },
      { label: 'Key limitation', value: 'Penalises upside', color: '#718096',
        text: `Sharpe treats upside volatility as bad. A stock that jumps +10% in a day gets penalised. The Sortino ratio (${fix2(m.sortino)}) only counts downside moves — often a fairer measure.` }
    ],
    sortino: [
      { label: 'Sortino Ratio', value: fix2(m.sortino), color: metricColors.sortino,
        text: `Sortino = (${pct(m.ann_return)} − ${pct(m.rf_ann)}) ÷ downside deviation = ${fix2(m.sortino)}. Only days where the stock lost money count toward the risk denominator.` },
      { label: 'vs Sharpe', value: `Sharpe ${fix2(m.sharpe)}`, color: '#d1d5db',
        text: `${ticker}'s Sortino (${fix2(m.sortino)}) is ${m.sortino > m.sharpe ? 'higher than' : 'lower than'} its Sharpe (${fix2(m.sharpe)}). ${m.sortino > m.sharpe ? 'Upside volatility exceeds downside — good asymmetry.' : 'Downside moves dominate total volatility — more left-tail risk.'}` },
      { label: 'When it matters', value: 'Downside-first investors', color: '#718096',
        text: `Risk-averse investors, pension funds, and wealth managers typically prefer Sortino. It rewards stocks that deliver returns without frequent large losses.` }
    ],
    treynor: [
      { label: 'Treynor Ratio', value: fix2(m.treynor), color: metricColors.treynor,
        text: `Treynor = (${pct(m.ann_return)} − ${pct(m.rf_ann)}) ÷ ${fix3(m.beta)} = ${fix2(m.treynor)}. Return per unit of systematic risk only — idiosyncratic risk is ignored.` },
      { label: 'When to use it', value: 'Diversified portfolio', color: '#d1d5db',
        text: `When ${ticker} is one holding in a diversified portfolio, idiosyncratic risk is already diversified away. Only beta (systematic) risk remains — making Treynor the right ratio to compare stocks.` },
      { label: 'vs Sharpe', value: `Sharpe ${fix2(m.sharpe)}`, color: '#718096',
        text: `${ticker}'s Sharpe (${fix2(m.sharpe)}) uses total volatility; Treynor (${fix2(m.treynor)}) uses beta. The gap reflects idiosyncratic risk that disappears when held in a portfolio.` }
    ],
    vol: [
      { label: 'Annualised volatility', value: pct(m.ann_vol), color: metricColors.vol,
        text: `${ticker} moves ±${(m.ann_vol*100).toFixed(1)}% per year on average (1 standard deviation). In a typical year, returns could range from ${pct(m.ann_return - m.ann_vol)} to ${pct(m.ann_return + m.ann_vol)}.` },
      { label: 'vs S&P 500', value: 'Market ~15–18%', color: '#d1d5db',
        text: `${ticker} at ${pct(m.ann_vol)} is ${m.ann_vol > 0.18 ? (m.ann_vol/0.165).toFixed(1) + 'x more volatile' : 'less volatile'} than the broad market. Higher volatility means wider return swings in both directions.` },
      { label: 'Daily equivalent', value: `±${(m.ann_vol/Math.sqrt(252)*100).toFixed(2)}% per day`, color: '#718096',
        text: `On a typical trading day, ${ticker} moves ±${(m.ann_vol/Math.sqrt(252)*100).toFixed(2)}%. That means on 2 out of 3 days, the move stays within this range.` },
      { label: 'Risk framing', value: `$${(m.ann_vol*10000).toFixed(0)} per $10K/year`, color: '#718096',
        text: `On a $10,000 position, annual volatility of ${pct(m.ann_vol)} means typical swings of ±$${(m.ann_vol*10000).toFixed(0)} per year.` }
    ],
    drawdown: [
      { label: 'Max Drawdown', value: `-${(m.max_dd*100).toFixed(2)}%`, color: '#ef4444',
        text: `The worst loss ${ticker} experienced in this period was ${(m.max_dd*100).toFixed(2)}% from peak to trough. An investor who bought at the peak would have been down this much before recovery.` },
      { label: 'Dollar impact', value: `-$${(m.max_dd*10000).toFixed(0)} per $10K`, color: '#ef4444',
        text: `On a $10,000 investment, this drawdown would mean a paper loss of $${(m.max_dd*10000).toFixed(0)}. Understanding the real dollar impact helps frame the emotional and practical risk of holding through a downturn.` },
      { label: 'Recovery required', value: `+${((1/(1-m.max_dd)-1)*100).toFixed(1)}% to recover`, color: '#f59e0b',
        text: `After a ${(m.max_dd*100).toFixed(1)}% loss, the stock needs to gain ${((1/(1-m.max_dd)-1)*100).toFixed(1)}% just to get back to the previous peak. Larger drawdowns require disproportionately larger recoveries.` },
      { label: 'Severity rating', value: m.max_dd < 0.10 ? 'Contained' : m.max_dd < 0.20 ? 'Moderate' : 'Severe', color: m.max_dd < 0.10 ? '#22c55e' : m.max_dd < 0.20 ? '#f59e0b' : '#ef4444',
        text: `Drawdowns below 10% are normal and contained. 10–20% is moderate and common in volatile stocks. Above 20% is severe and tests investor conviction.` }
    ],
    var95: [
      { label: 'VaR 95%', value: `-${(m.var95*100).toFixed(2)}%`, color: '#ef4444',
        text: `On 95% of trading days, ${ticker} loses no more than ${(m.var95*100).toFixed(2)}%. On the worst 5% of days — roughly 13 days per year — losses exceed this level.` },
      { label: 'Dollar framing', value: `-$${(m.var95*10000).toFixed(0)} per $10K`, color: '#ef4444',
        text: `On a $10,000 position, a VaR 95% event means a single-day loss of up to $${(m.var95*10000).toFixed(0)}. This happens roughly once a month on average.` },
      { label: 'Methodology', value: 'Historical simulation', color: '#d1d5db',
        text: `This reads directly from the 5th percentile of actual historical daily returns — no assumptions about distribution shape. It reflects what ${ticker} has actually done.` }
    ],
    var99: [
      { label: 'VaR 99%', value: `-${(m.var99*100).toFixed(2)}%`, color: '#ef4444',
        text: `Only 1% of trading days — roughly 2–3 days per year — produce losses worse than ${(m.var99*100).toFixed(2)}%. These are rare but severe events.` },
      { label: 'Gap vs VaR 95%', value: `+${((m.var99-m.var95)*100).toFixed(2)}%`, color: '#f59e0b',
        text: `The gap between VaR 99% and VaR 95% is ${((m.var99-m.var95)*100).toFixed(2)}%. A wide gap indicates fat tails — when bad days happen, they tend to be much worse than a normal distribution would predict.` },
      { label: 'Important caveat', value: 'Not the worst case', color: '#718096',
        text: `VaR 99% only tells you the threshold, not the average loss beyond it. In the worst 1% of days, losses could be far larger. CVaR (Expected Shortfall) would show the average of those tail losses.` }
    ],
    ir: [
      { label: 'Information Ratio', value: fix2(m.ir), color: metricColors.ir,
        text: `IR = Active Return ÷ Tracking Error = ${fix2(m.ir)}. Active return is the average daily outperformance vs S&P 500; tracking error is how consistently it outperforms.` },
      { label: 'Benchmark', value: '> 0.5 = Good', color: '#d1d5db',
        text: `Professional fund managers typically target IR above 0.5. Above 1.0 is considered exceptional. ${ticker}'s ${fix2(m.ir)} puts it ${m.ir > 0.5 ? 'in the good range' : 'below the professional threshold'}.` },
      { label: 'What it adds to alpha', value: `Alpha ${pct(m.alpha)}`, color: '#718096',
        text: `Alpha tells you the size of outperformance; IR tells you the reliability. ${ticker} generates ${pct(m.alpha)} alpha, and at IR ${fix2(m.ir)} that outperformance is ${m.ir > 0.5 ? 'consistent' : 'lumpy and unreliable'}.` }
    ]
  };

  const cards = cardDefs[key];
  if (cards) openMetricModal(key.toUpperCase() + ' — ' + ticker, leftHTML, cards);
}"""

if old2 in content:
    content = content.replace(old2, new2)
    print('explainMetric body: OK')
else:
    print('explainMetric body: ERROR not found')

open('templates/index.html', 'w').write(result)

# Now do chart explanations
content = open('templates/index.html').read()

old3 = """// ─────────────────────────────────────────────
//  Chart explanation modals
// ─────────────────────────────────────────────
function explainChart(key, ticker, m) {
  const defs = {
    perf: {
      title: 'Price Performance Chart', sub: 'Both series rebased to 100 for direct comparison',
      cards: [
        { label: 'What it shows', value: 'Rebased prices', color: '#d1d5db', text: 'Both lines start at 100 regardless of actual price. This makes the comparison fair — a $3 stock and a $300 stock are on equal footing.' },
        { label: `${ticker} line`, value: pct(m.ann_return), color: '#15803d',
          text: `The green line is ${ticker}. It ends at ${((1+m.ann_return)*100).toFixed(1)} — meaning a $100 investment became $${((1+m.ann_return)*100).toFixed(0)} over this period.` },
        { label: 'S&P 500 line', value: pct(m.bench_return), color: '#ffffff',
          text: `The white dashed line is the S&P 500. When the green line is above it, ${ticker} is outperforming.` },
        { label: 'Gap', value: pct(m.ann_return - m.bench_return), color: (m.ann_return-m.bench_return) >= 0 ? '#22c55e' : '#ef4444',
          text: `The vertical gap between lines represents active return. A widening gap is positive — ${ticker} is pulling ahead of the market.` }
      ]
    },
    beta: {
      title: 'Rolling 60-Day Beta Chart', sub: 'Beta recalculated every 60 trading days to show how risk evolves',
      cards: [
        { label: 'What it shows', value: 'Beta over time', color: '#d1d5db',
          text: 'Beta is not static. This chart calculates beta fresh every 60 days using a rolling window, showing how the stock\'s market sensitivity has changed.' },
        { label: 'Reference line', value: 'β = 1.0', color: '#ffffff',
          text: 'The dotted white line marks beta = 1. Above it means the stock amplifies market moves; below means it dampens them.' },
        { label: 'Current beta', value: fix3(m.beta), color: '#d1d5db',
          text: `The current 60-day beta is ${fix3(m.beta)}. If beta has been trending ${m.beta > 1 ? 'up' : 'down'} recently, the stock is becoming ${m.beta > 1 ? 'more aggressive' : 'more defensive'}.` },
        { label: 'Why it matters', value: 'Risk is dynamic', color: '#718096',
          text: 'A stock that was defensive six months ago may be aggressive today. Rolling beta catches these regime changes that a static single-number beta misses.' }
      ]
    },
    dist: {
      title: 'Daily Return Distribution', sub: 'Histogram of all daily returns over the analysis period',
      cards: [
        { label: 'What it shows', value: 'Return frequency', color: '#d1d5db',
          text: 'Each bar represents how often the stock returned within that range in a single day. Tall central bars = most days are small moves.' },
        { label: 'Green vs red', value: 'Positive vs negative', color: '#22c55e',
          text: 'Green bars are positive return days; red bars are negative. If the distribution is skewed right, the stock has more large positive days than large negative ones.' },
        { label: 'Fat tails', value: 'Extreme moves', color: '#f59e0b',
          text: `VaR 99% of ${(m.var99*100).toFixed(2)}% represents the left tail. If bars extend far left, extreme loss days happen more often than a normal distribution predicts.` },
        { label: 'Volatility', value: pct(m.ann_vol), color: '#d1d5db',
          text: `A narrow, tall distribution means low volatility (${pct(m.ann_vol)} annualised). A flat, wide distribution means the stock is very volatile.` }
      ]
    },
    dd: {
      title: 'Drawdown Over Time', sub: 'How far below its previous peak the stock was at each point',
      cards: [
        { label: 'What it shows', value: 'Loss from peak', color: '#d1d5db',
          text: 'When the line is at 0, the stock is at an all-time high for the period. Every dip below 0 shows a loss from the previous peak.' },
        { label: 'Max Drawdown', value: `-${(m.max_dd*100).toFixed(2)}%`, color: '#ef4444',
          text: `The deepest point on this chart is the max drawdown of -${(m.max_dd*100).toFixed(2)}%. This is the worst an investor would have felt if they bought at the peak.` },
        { label: 'Recovery speed', value: 'Resilience signal', color: '#d1d5db',
          text: 'How quickly the line returns to 0 after a drawdown matters. Fast recovery = resilient stock. Extended time below 0 = slow recovery from losses.' },
        { label: 'Current position', value: 'End of period', color: '#718096',
          text: 'If the chart ends near 0, the stock recovered. If it ends below 0, it\'s still in a drawdown relative to its peak during this period.' }
      ]
    },
    sml: {
      title: 'CAPM Security Market Line', sub: 'Where this stock sits relative to where theory says it should',
      cards: [
        { label: 'The line', value: 'Theoretical returns', color: '#d1d5db',
          text: 'The dotted line is the Security Market Line — for any given beta, it shows what CAPM says you should expect as return. All "fairly priced" assets should sit on it.' },
        { label: `${ticker} actual`, value: pct(m.ann_return), color: m.alpha >= 0 ? '#22c55e' : '#ef4444',
          text: `The ${m.alpha >= 0 ? 'green' : 'red'} dot is where ${ticker} actually sits. It's ${m.alpha >= 0 ? 'above' : 'below'} the line — meaning it ${m.alpha >= 0 ? 'delivered more' : 'delivered less'} than CAPM predicted.` },
        { label: 'CAPM predicted', value: pct(m.capm_exp), color: '#d1d5db',
          text: `The triangle shows where ${ticker} "should" be given its beta of ${fix3(m.beta)}. The gap between the dot and triangle is Jensen's Alpha: ${pct(m.alpha)}.` },
        { label: 'The gap', value: `Alpha ${pct(m.alpha)}`, color: m.alpha >= 0 ? '#22c55e' : '#ef4444',
          text: `A dot above the line = positive alpha = genuine outperformance beyond what systematic risk alone explains. This is what every active manager aims for.` }
      ]
    }
  };
  const d = defs[key];
  if (d) openModal(d.title, d.sub, d.cards);
}"""

new3 = """// ─────────────────────────────────────────────
//  Chart explanation modals — two-panel with re-rendered charts
// ─────────────────────────────────────────────
function explainChart(key, ticker, m) {
  const chartHTML = `<div id="modalChart" style="height:320px"></div>`;

  const cardDefs = {
    perf: [
      { label: `${ticker} annualised return`, value: pct(m.ann_return), color: '#15803d',
        text: `${ticker} delivered ${pct(m.ann_return)} per year. A $100 investment at the start became $${((1+m.ann_return)*100).toFixed(0)} by the end of the period.` },
      { label: 'S&P 500 return', value: pct(m.bench_return), color: '#ffffff',
        text: `The S&P 500 returned ${pct(m.bench_return)} over the same period. The gap between the green line and white line shows active outperformance.` },
      { label: 'Active return', value: pct(m.ann_return - m.bench_return), color: (m.ann_return-m.bench_return) >= 0 ? '#22c55e' : '#ef4444',
        text: `${ticker} ${m.ann_return > m.bench_return ? 'outperformed' : 'underperformed'} the market by ${Math.abs((m.ann_return-m.bench_return)*100).toFixed(2)}% per year. Both lines start at 100 so comparison is fair regardless of share price.` },
      { label: 'What to look for', value: 'Line divergence', color: '#718096',
        text: `When the green line pulls away from the white line, ${ticker} is outperforming. When the gap narrows or reverses, it is underperforming. The slope of each line shows the return rate at any point in time.` }
    ],
    beta: [
      { label: 'Current 60-day beta', value: fix3(m.beta), color: '#d1d5db',
        text: `The most recent 60-day beta is ${fix3(m.beta)}. This means ${ticker} currently moves ${(m.beta*100).toFixed(1)}% for every 1% move in the S&P 500.` },
      { label: 'Beta = 1 reference', value: 'Market neutral', color: '#718096',
        text: `The dotted line at β=1 is the reference. When ${ticker}'s beta is above 1, it amplifies market moves. Below 1, it dampens them.` },
      { label: 'Beta trend', value: 'Dynamic risk', color: '#d1d5db',
        text: `Rolling beta reveals regime changes. If beta has risen recently, ${ticker} has become more market-sensitive. A falling beta suggests it is decoupling from the market — either defensively or idiosyncratically.` },
      { label: 'Why 60-day window', value: 'Recency vs noise', color: '#718096',
        text: `60 trading days (~3 months) balances recency with statistical reliability. Shorter windows are noisier; longer windows miss current regime changes.` }
    ],
    dist: [
      { label: 'Annualised volatility', value: pct(m.ann_vol), color: '#d1d5db',
        text: `The width of this distribution reflects ${ticker}'s volatility of ${pct(m.ann_vol)}. A wider, flatter shape means more extreme daily moves in both directions.` },
      { label: 'VaR 95% left tail', value: `-${(m.var95*100).toFixed(2)}%`, color: '#ef4444',
        text: `The left tail beyond -${(m.var95*100).toFixed(2)}% represents days where ${ticker} lost more than the VaR 95% threshold — roughly 13 days per year.` },
      { label: 'VaR 99% extreme', value: `-${(m.var99*100).toFixed(2)}%`, color: '#ef4444',
        text: `Beyond -${(m.var99*100).toFixed(2)}%, you enter the 1% tail — roughly 2-3 days per year of extreme losses. These are the black-swan days.` },
      { label: 'Shape interpretation', value: 'Normal vs fat-tailed', color: '#718096',
        text: `If the distribution has tall thin bars in the centre and bars extending far to the left, ${ticker} has fat tails — losses are more extreme than a normal distribution would predict.` }
    ],
    dd: [
      { label: 'Max Drawdown', value: `-${(m.max_dd*100).toFixed(2)}%`, color: '#ef4444',
        text: `The deepest point on this chart is -${(m.max_dd*100).toFixed(2)}%. An investor who bought at the peak before this trough would have been down this much before recovery.` },
      { label: 'Recovery required', value: `+${((1/(1-m.max_dd)-1)*100).toFixed(1)}%`, color: '#f59e0b',
        text: `After a ${(m.max_dd*100).toFixed(1)}% peak-to-trough loss, ${ticker} needed to gain ${((1/(1-m.max_dd)-1)*100).toFixed(1)}% just to recover. Larger drawdowns require disproportionately larger rebounds.` },
      { label: 'Time at zero', value: 'At all-time highs', color: '#22c55e',
        text: `When the line is at 0, ${ticker} is at its peak for the period. The more time spent near 0, the fewer buying-at-top scenarios investors face.` },
      { label: 'What to look for', value: 'Depth and duration', color: '#718096',
        text: `Both the depth of drawdowns and how long they last matter. A quick -20% that recovered in days is less damaging psychologically and financially than a slow -15% over 18 months.` }
    ],
    sml: [
      { label: `${ticker} actual position`, value: pct(m.ann_return), color: m.alpha >= 0 ? '#22c55e' : '#ef4444',
        text: `${ticker} sits at beta ${fix3(m.beta)}, return ${pct(m.ann_return)} on the chart. The ${m.alpha >= 0 ? 'green' : 'red'} dot is ${m.alpha >= 0 ? 'above' : 'below'} the Security Market Line.` },
      { label: 'CAPM prediction', value: pct(m.capm_exp), color: '#d1d5db',
        text: `Given beta ${fix3(m.beta)}, CAPM says ${ticker} should return ${pct(m.capm_exp)}. The blue triangle marks this theoretical point on the line.` },
      { label: "Jensen's Alpha", value: pct(m.alpha), color: m.alpha >= 0 ? '#22c55e' : '#ef4444',
        text: `The vertical gap between the green dot and the blue triangle is ${pct(m.alpha)}. Above the line = outperforming for its risk level. Below = underperforming.` },
      { label: 'The Security Market Line', value: 'Fair value line', color: '#718096',
        text: `Every point on the dotted line represents a "fairly priced" asset — one that earns exactly what its beta justifies. Assets above the line are generating alpha; below the line are destroying value on a risk-adjusted basis.` }
    ]
  };

  const renderers = {
    perf: (c) => () => {
      Plotly.newPlot('modalChart', [
        { x: c.dates, y: c.stock_rebased, name: ticker, line: { color: '#15803d', width: 2.5 }, type: 'scatter' },
        { x: c.dates, y: c.bench_rebased, name: 'S&P 500', line: { color: '#ffffff', width: 2, dash: 'dot' }, type: 'scatter' }
      ], { ...PL, margin: { t:10,r:10,b:40,l:50 } }, CFG);
    },
    beta: (c) => () => {
      Plotly.newPlot('modalChart', [
        { x: c.roll_dates, y: c.roll_betas, name: 'Beta', line: { color: '#d1d5db', width: 2.5 }, type: 'scatter' },
        { x: [c.roll_dates[0], c.roll_dates[c.roll_dates.length-1]], y: [1,1], name: 'β=1', line: { color: 'rgba(255,255,255,0.3)', dash: 'dot', width: 1.5 }, type: 'scatter' }
      ], { ...PL, margin: { t:10,r:10,b:40,l:50 } }, CFG);
    },
    dist: (c) => () => {
      Plotly.newPlot('modalChart', [{
        x: c.dist_labels, y: c.dist_values, type: 'bar',
        marker: { color: c.dist_labels.map(l => parseFloat(l) >= 0 ? 'rgba(21,128,61,0.8)' : 'rgba(239,68,68,0.8)') }
      }], { ...PL, xaxis: { ...PL.xaxis, title: 'Daily Return %', type: 'linear' }, showlegend: false, margin: { t:10,r:10,b:40,l:50 } }, CFG);
    },
    dd: (c) => () => {
      Plotly.newPlot('modalChart', [{
        x: c.dd_dates, y: c.dd_series, fill: 'tozeroy',
        fillcolor: 'rgba(255,255,255,0.06)', line: { color: '#ffffff', width: 2.5 }, type: 'scatter', showlegend: false
      }], { ...PL, yaxis: { ...PL.yaxis, title: 'Drawdown %' }, margin: { t:10,r:10,b:40,l:55 } }, CFG);
    },
    sml: (c) => () => {
      Plotly.newPlot('modalChart', [
        { x: c.sml_betas, y: c.sml_returns.map(v => v*100), name: 'SML', line: { color: 'rgba(255,255,255,0.3)', dash: 'dot', width: 1.5 }, type: 'scatter' },
        { x: [c.stock_beta], y: [c.stock_return*100], name: `${ticker} actual`, mode: 'markers', marker: { color: m.alpha >= 0 ? '#22c55e' : '#ef4444', size: 14 } },
        { x: [c.stock_beta], y: [c.capm_return*100], name: 'CAPM predicted', mode: 'markers', marker: { color: '#d1d5db', size: 11, symbol: 'triangle-up' } }
      ], { ...PL, xaxis: { ...PL.xaxis, title: 'Beta', type: 'linear' }, yaxis: { ...PL.yaxis, title: 'Return (%)' }, hovermode: 'closest', margin: { t:10,r:10,b:40,l:55 } }, CFG);
    }
  };

  // Get chart data from state
  const c = state.pricing && state.pricing.pricing ? state.pricing.pricing.charts : null;
  if (!c) return;

  const cards = cardDefs[key];
  const renderer = renderers[key] ? renderers[key](c) : null;
  if (cards) openChartModal(`${ticker} — ${key.toUpperCase()} Chart`, chartHTML, cards, renderer);
}"""

if old3 in content:
    content = content.replace(old3, new3)
    print('explainChart: OK')
else:
    print('explainChart: ERROR not found')

open('templates/index.html', 'w').write(content)
print('Done')
