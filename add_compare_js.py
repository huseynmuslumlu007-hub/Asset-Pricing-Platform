content = open('templates/index.html').read()

old = """\'use strict\';"""

new = """\'use strict\';

// ─────────────────────────────────────────────
//  Compare Module
// ─────────────────────────────────────────────
let compareMode = 'stocks';
let compareData = null;

function setCompareMode(mode) {
  compareMode = mode;
  document.getElementById('modeStocks').classList.toggle('active', mode === 'stocks');
  document.getElementById('modePortfolios').classList.toggle('active', mode === 'portfolios');
  document.getElementById('compareResults').style.display = 'none';
  renderCompareInputs();
}

function renderCompareInputs() {
  const el = document.getElementById('compareInputs');
  if (compareMode === 'stocks') {
    el.innerHTML = `
      <div class="compare-input-side">
        <div class="compare-input-label">Stock A</div>
        <input id="cmpTicker1" class="compare-ticker-input" type="text" placeholder="e.g. AAPL" autocomplete="off"/>
      </div>
      <div class="compare-input-side">
        <div class="compare-input-label">Stock B</div>
        <input id="cmpTicker2" class="compare-ticker-input" type="text" placeholder="e.g. NVDA" autocomplete="off"/>
      </div>`;
  } else {
    el.innerHTML = `
      <div class="compare-input-side">
        <div class="compare-input-label">Portfolio A</div>
        <div id="cmpPortRowsLeft" class="port-compare-rows"></div>
        <button class="btn-ghost" style="margin-top:8px;font-size:12px" onclick="addCmpPortRow('Left')">+ Add ticker</button>
      </div>
      <div class="compare-input-side">
        <div class="compare-input-label">Portfolio B</div>
        <div id="cmpPortRowsRight" class="port-compare-rows"></div>
        <button class="btn-ghost" style="margin-top:8px;font-size:12px" onclick="addCmpPortRow('Right')">+ Add ticker</button>
      </div>`;
    addCmpPortRow('Left'); addCmpPortRow('Left'); addCmpPortRow('Left');
    addCmpPortRow('Right'); addCmpPortRow('Right'); addCmpPortRow('Right');
  }
}

function addCmpPortRow(side) {
  const rows = document.getElementById('cmpPortRows' + side);
  if (!rows || rows.children.length >= 10) return;
  const div = document.createElement('div');
  div.className = 'port-row';
  div.innerHTML = '<input type="text" placeholder="Ticker" class="port-ticker" maxlength="10"/><input type="number" placeholder="Weight %" class="port-weight" min="0" max="100" step="0.1"/><button class="btn-remove" onclick="this.parentElement.remove()">×</button>';
  rows.appendChild(div);
}

async function runCompare() {
  const btn = document.getElementById('compareRunBtn');
  btn.disabled = true; btn.textContent = 'Loading…';
  const period = document.getElementById('comparePeriod').value;

  try {
    if (compareMode === 'stocks') {
      const t1 = document.getElementById('cmpTicker1').value.trim().toUpperCase();
      const t2 = document.getElementById('cmpTicker2').value.trim().toUpperCase();
      if (!t1 || !t2) { alert('Enter both tickers.'); return; }

      document.getElementById('compareResults').style.display = 'grid';
      document.getElementById('compareLeft').innerHTML = '<div class="state-loading"><div class="spinner"></div><div>Analysing ' + t1 + '…</div></div>';
      document.getElementById('compareRight').innerHTML = '<div class="state-loading"><div class="spinner"></div><div>Analysing ' + t2 + '…</div></div>';
      document.getElementById('compareTableWrap').innerHTML = '';

      const res = await fetch('/api/compare/stocks', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ticker1: t1, ticker2: t2, period})
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      compareData = data;
      renderStockCompareSide('compareLeft', data.left);
      renderStockCompareSide('compareRight', data.right);
      renderStockCompareTable(data.left, data.right);

    } else {
      const getRows = (side) => {
        const rows = document.querySelectorAll('#cmpPortRows' + side + ' .port-row');
        const out = [];
        rows.forEach(r => {
          const t = r.querySelector('.port-ticker').value.trim().toUpperCase();
          const w = parseFloat(r.querySelector('.port-weight').value);
          if (t) out.push({ticker: t, weight: isNaN(w) ? 0 : w / 100});
        });
        return out;
      };
      const left = getRows('Left'), right = getRows('Right');
      if (left.length < 2 || right.length < 2) { alert('Each portfolio needs at least 2 tickers.'); return; }

      document.getElementById('compareResults').style.display = 'grid';
      document.getElementById('compareLeft').innerHTML = '<div class="state-loading"><div class="spinner"></div><div>Analysing Portfolio A…</div></div>';
      document.getElementById('compareRight').innerHTML = '<div class="state-loading"><div class="spinner"></div><div>Analysing Portfolio B…</div></div>';
      document.getElementById('compareTableWrap').innerHTML = '';

      const res = await fetch('/api/compare/portfolios', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({left, right, period})
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      compareData = data;
      renderPortCompareSide('compareLeft', data.left, 'A');
      renderPortCompareSide('compareRight', data.right, 'B');
      renderPortCompareTable(data.left, data.right);
    }
  } catch(err) {
    document.getElementById('compareLeft').innerHTML = '<div class="state-error">⚠ ' + err.message + '</div>';
    document.getElementById('compareRight').innerHTML = '';
  } finally {
    btn.disabled = false; btn.textContent = 'Run Comparison';
  }
}

// ── Stock compare side ────────────────────────────────────────────────────────
function renderStockCompareSide(elId, d) {
  const m = d.pricing.metrics, f = d.factors.ff5, s = d.score, t = d.ticker;
  const sc = s.composite >= 75 ? '#22c55e' : s.composite >= 60 ? '#22c55e' : s.composite >= 45 ? '#f59e0b' : '#ef4444';
  const fN = {MKT_RF:'Market',SMB:'Size',HML:'Value',RMW:'Profitability',CMA:'Investment'};
  const el = document.getElementById(elId);
  el.innerHTML = `
    <div class="compare-side-title">${t}</div>

    <div class="cmp-score-row">
      ${scoreArc(s.composite, sc)}
      <div>
        <div style="font-size:13px;font-weight:600;color:${sc};margin-bottom:4px">${s.verdict}</div>
        <div style="font-size:11px;color:var(--muted)">Investment Score</div>
      </div>
    </div>

    <div class="section-head">Pricing Metrics</div>
    <div class="cmp-metrics">
      <div class="mc" onclick='showMetric("beta","${t}",${JSON.stringify(m)})'>
        <div class="mc-l">Beta</div>
        <div class="mc-v ${m.beta>1.2?'neg':m.beta<0.8?'pos':'neu'}">${fix3(m.beta)}</div>
      </div>
      <div class="mc" onclick='showMetric("return","${t}",${JSON.stringify(m)})'>
        <div class="mc-l">Return (Ann.)</div>
        <div class="mc-v ${cls(m.ann_return)}">${pct(m.ann_return)}</div>
      </div>
      <div class="mc" onclick='showMetric("alpha","${t}",${JSON.stringify(m)})'>
        <div class="mc-l">Alpha</div>
        <div class="mc-v ${cls(m.alpha)}">${pct(m.alpha)}</div>
      </div>
      <div class="mc" onclick='showMetric("sharpe","${t}",${JSON.stringify(m)})'>
        <div class="mc-l">Sharpe</div>
        <div class="mc-v ${m.sharpe>1?'pos':m.sharpe>0.5?'amb':'neg'}">${fix2(m.sharpe)}</div>
      </div>
      <div class="mc" onclick='showMetric("sortino","${t}",${JSON.stringify(m)})'>
        <div class="mc-l">Sortino</div>
        <div class="mc-v ${m.sortino>1?'pos':m.sortino>0.5?'amb':'neg'}">${fix2(m.sortino)}</div>
      </div>
      <div class="mc" onclick='showMetric("vol","${t}",${JSON.stringify(m)})'>
        <div class="mc-l">Volatility</div>
        <div class="mc-v ${m.ann_vol>0.35?'neg':m.ann_vol>0.2?'amb':'pos'}">${pct(m.ann_vol)}</div>
      </div>
      <div class="mc" onclick='showMetric("drawdown","${t}",${JSON.stringify(m)})'>
        <div class="mc-l">Max Drawdown</div>
        <div class="mc-v neg">-${(m.max_dd*100).toFixed(2)}%</div>
      </div>
      <div class="mc" onclick='showMetric("var95","${t}",${JSON.stringify(m)})'>
        <div class="mc-l">VaR 95%</div>
        <div class="mc-v neg">-${(m.var95*100).toFixed(2)}%</div>
      </div>
      <div class="mc" onclick='showMetric("ir","${t}",${JSON.stringify(m)})'>
        <div class="mc-l">Info Ratio</div>
        <div class="mc-v ${m.ir>0.5?'pos':m.ir>0?'amb':'neg'}">${fix2(m.ir)}</div>
      </div>
    </div>

    <div class="section-head">Factor Profile (FF5)</div>
    <div class="cmp-metrics">
      ${Object.entries(f.loadings).map(([k,v])=>`
        <div class="mc" onclick='showFactor("${k}","${t}",${JSON.stringify(f)})'>
          <div class="mc-l">${fN[k]||k}</div>
          <div class="mc-v ${v>0?'pos':'neg'}">${fix3(v)}</div>
        </div>`).join('')}
      <div class="mc" onclick='showFactor("alpha","${t}",${JSON.stringify(f)})'>
        <div class="mc-l">Residual α</div>
        <div class="mc-v ${cls(f.alpha)}">${pct(f.alpha)}</div>
      </div>
      <div class="mc" onclick='showFactor("r2","${t}",${JSON.stringify(f)})'>
        <div class="mc-l">R² FF5</div>
        <div class="mc-v neu">${(f.r2*100).toFixed(1)}%</div>
      </div>
    </div>

    <div class="section-head">Score Breakdown</div>
    <div class="score-components">
      ${Object.entries(s.scores).map(([k,v])=>{
        const color=v>=65?'#22c55e':v>=45?'#f59e0b':'#ef4444';
        const lb={valuation:'Valuation',momentum:'Momentum',quality:'Quality',risk_adjusted:'Risk-Adj',factor:'Factor'};
        return `<div class="score-row">
          <div class="score-row-label"><span>${lb[k]||k}</span><span class="score-weight">${(s.weights[k]*100).toFixed(0)}%</span></div>
          <div class="score-bar-wrap"><div class="score-bar" style="width:${v}%;background:${color}"></div></div>
          <div class="score-row-val" style="color:${color}">${v}</div>
          <div class="score-expl">${s.explanations[k]}</div>
        </div>`;
      }).join('')}
    </div>`;

  setTimeout(() => {
    const c = d.pricing.charts;
    const chartId = 'cmpChart_' + elId;
    el.innerHTML += `<div class="section-head" style="margin-top:8px">Price Performance</div><div id="${chartId}" style="height:200px"></div>`;
    Plotly.newPlot(chartId, [
      {x:c.dates, y:c.stock_rebased, name:t, line:{color:'#15803d',width:2}, type:'scatter'},
      {x:c.dates, y:c.bench_rebased, name:'S&P 500', line:{color:'rgba(255,255,255,0.3)',width:1.5,dash:'dot'}, type:'scatter'}
    ], lay({margin:{t:10,r:10,b:30,l:45}}), CFG);
  }, 80);
}

// ── Portfolio compare side ────────────────────────────────────────────────────
function renderPortCompareSide(elId, data, label) {
  const m = data.metrics, c = data.charts;
  const s = data.portfolio_score;
  const sc = s.composite>=65?'#22c55e':s.composite>=45?'#f59e0b':'#ef4444';
  const el = document.getElementById(elId);
  el.innerHTML = `
    <div class="compare-side-title">Portfolio ${label}</div>

    <div class="cmp-score-row">
      ${scoreArc(s.composite, sc)}
      <div>
        <div style="font-size:13px;font-weight:600;color:${sc};margin-bottom:4px">${s.verdict}</div>
        <div style="font-size:11px;color:var(--muted)">Portfolio Score</div>
      </div>
    </div>

    <div class="section-head">Portfolio Metrics</div>
    <div class="cmp-metrics">
      <div class="mc"><div class="mc-l">Return</div><div class="mc-v ${cls(m.ann_return)}">${pct(m.ann_return)}</div></div>
      <div class="mc"><div class="mc-l">Volatility</div><div class="mc-v ${m.ann_vol>0.25?'neg':'amb'}">${pct(m.ann_vol)}</div></div>
      <div class="mc"><div class="mc-l">Sharpe</div><div class="mc-v ${m.sharpe>1?'pos':m.sharpe>0.5?'amb':'neg'}">${fix2(m.sharpe)}</div></div>
      <div class="mc"><div class="mc-l">Beta</div><div class="mc-v neu">${fix3(m.beta)}</div></div>
      <div class="mc"><div class="mc-l">Alpha</div><div class="mc-v ${cls(m.alpha)}">${pct(m.alpha)}</div></div>
      <div class="mc"><div class="mc-l">Max DD</div><div class="mc-v neg">-${(m.max_dd*100).toFixed(2)}%</div></div>
    </div>

    <div class="section-head">Holdings</div>
    <table class="holdings-table">
      <thead><tr><th>Ticker</th><th>Weight</th><th>Return</th><th>Sharpe</th></tr></thead>
      <tbody>
        ${data.holdings.map(h=>`<tr>
          <td class="sym-cell">${h.ticker}</td>
          <td>${(h.weight*100).toFixed(1)}%</td>
          <td class="${cls(h.ann_return)}">${pct(h.ann_return)}</td>
          <td class="${h.sharpe>1?'pos':h.sharpe>0.5?'amb':'neg'}">${fix2(h.sharpe)}</td>
        </tr>`).join('')}
      </tbody>
    </table>`;

  setTimeout(() => {
    const chartId = 'cmpPortChart_' + elId;
    el.innerHTML += `<div class="section-head">Performance</div><div id="${chartId}" style="height:200px"></div>`;
    Plotly.newPlot(chartId, [
      {x:c.dates, y:c.port_cumulative, name:'Portfolio '+label, line:{color:'#15803d',width:2}, type:'scatter'},
      {x:c.dates, y:c.bench_cumulative, name:'S&P 500', line:{color:'rgba(255,255,255,0.3)',width:1.5,dash:'dot'}, type:'scatter'}
    ], lay({margin:{t:10,r:10,b:30,l:45}}), CFG);
  }, 80);
}

// ── Stock comparison table ────────────────────────────────────────────────────
function renderStockCompareTable(left, right) {
  const m1 = left.pricing.metrics, m2 = right.pricing.metrics;
  const f1 = left.factors.ff5, f2 = right.factors.ff5;
  const s1 = left.score, s2 = right.score;
  const t1 = left.ticker, t2 = right.ticker;

  function winner(v1, v2, higherBetter=true) {
    if (higherBetter) return v1 > v2 ? t1 : v2 > v1 ? t2 : 'Tie';
    return v1 < v2 ? t1 : v2 < v1 ? t2 : 'Tie';
  }

  function winBadge(v1, v2, higherBetter=true) {
    const w = winner(v1, v2, higherBetter);
    if (w === 'Tie') return '<span style="font-size:10px;color:var(--muted)">Tie</span>';
    return `<span class="cmp-winner">${w} ✓</span>`;
  }

  const rows = [
    {
      metric: 'Investment Score', v1: s1.composite, v2: s2.composite, higherBetter: true,
      fmt: v => v + '/100',
      explain: (w,l) => `${w} scores higher overall across valuation, momentum, quality, and risk-adjusted return signals. ${l} trails primarily on ${Object.entries(w===t1?s1.scores:s2.scores).sort((a,b)=>a[1]-b[1])[0][0]}.`
    },
    {
      metric: 'Annualised Return', v1: m1.ann_return, v2: m2.ann_return, higherBetter: true,
      fmt: v => pct(v),
      explain: (w,l) => `${w} delivered ${pct(w===t1?m1.ann_return:m2.ann_return)} vs ${pct(w===t1?m2.ann_return:m1.ann_return)} for ${l}. Raw return advantage of ${pct(Math.abs(m1.ann_return-m2.ann_return))}.`
    },
    {
      metric: 'Sharpe Ratio', v1: m1.sharpe, v2: m2.sharpe, higherBetter: true,
      fmt: v => fix2(v),
      explain: (w,l) => `${w} generates more return per unit of total risk (Sharpe ${fix2(w===t1?m1.sharpe:m2.sharpe)} vs ${fix2(w===t1?m2.sharpe:m1.sharpe)}). On a risk-adjusted basis, ${w} is the stronger performer.`
    },
    {
      metric: 'Sortino Ratio', v1: m1.sortino, v2: m2.sortino, higherBetter: true,
      fmt: v => fix2(v),
      explain: (w,l) => `${w} handles downside volatility better. Its Sortino of ${fix2(w===t1?m1.sortino:m2.sortino)} means fewer large negative days relative to the return generated.`
    },
    {
      metric: "Jensen's Alpha", v1: m1.alpha, v2: m2.alpha, higherBetter: true,
      fmt: v => pct(v),
      explain: (w,l) => `${w} generates ${pct(Math.abs(m1.alpha-m2.alpha))} more alpha above CAPM expectations. It is delivering more return than its systematic risk level requires.`
    },
    {
      metric: 'FF5 Residual Alpha', v1: f1.alpha, v2: f2.alpha, higherBetter: true,
      fmt: v => pct(v),
      explain: (w,l) => `After stripping out all five Fama-French factors, ${w} retains ${pct(w===t1?f1.alpha:f2.alpha)} of genuine stock-specific return. ${l} at ${pct(w===t1?f2.alpha:f1.alpha)} has less idiosyncratic outperformance.`
    },
    {
      metric: 'Volatility', v1: m1.ann_vol, v2: m2.ann_vol, higherBetter: false,
      fmt: v => pct(v),
      explain: (w,l) => `${w} carries less total price risk (${pct(w===t1?m1.ann_vol:m2.ann_vol)} annualised vol vs ${pct(w===t1?m2.ann_vol:m1.ann_vol)} for ${l}). Lower volatility means smoother returns and smaller position-size swings.`
    },
    {
      metric: 'Max Drawdown', v1: m1.max_dd, v2: m2.max_dd, higherBetter: false,
      fmt: v => '-' + (v*100).toFixed(2) + '%',
      explain: (w,l) => `${w} experienced a shallower worst-case loss (${((w===t1?m1.max_dd:m2.max_dd)*100).toFixed(1)}% vs ${((w===t1?m2.max_dd:m1.max_dd)*100).toFixed(1)}% for ${l}). Smaller drawdowns require less recovery to get back to break-even.`
    },
    {
      metric: 'Beta', v1: m1.beta, v2: m2.beta, higherBetter: false,
      fmt: v => fix3(v),
      explain: (w,l) => `${w} has lower systematic risk (beta ${fix3(w===t1?m1.beta:m2.beta)} vs ${fix3(w===t1?m2.beta:m1.beta)}). It amplifies market moves less, making it more defensive in downturns.`
    },
    {
      metric: 'Information Ratio', v1: m1.ir, v2: m2.ir, higherBetter: true,
      fmt: v => fix2(v),
      explain: (w,l) => `${w} outperforms its benchmark more consistently (IR ${fix2(w===t1?m1.ir:m2.ir)} vs ${fix2(w===t1?m2.ir:m1.ir)}). Higher IR means the alpha is reliable, not a one-off.`
    },
    {
      metric: 'Valuation Score', v1: s1.scores.valuation, v2: s2.scores.valuation, higherBetter: true,
      fmt: v => v + '/100',
      explain: (w,l) => `${w} is more attractively valued on traditional multiples (score ${w===t1?s1.scores.valuation:s2.scores.valuation} vs ${w===t1?s2.scores.valuation:s1.scores.valuation}). ${l} trades at a higher premium to fundamentals.`
    },
    {
      metric: 'Momentum Score', v1: s1.scores.momentum, v2: s2.scores.momentum, higherBetter: true,
      fmt: v => v + '/100',
      explain: (w,l) => `${w} has stronger price momentum across 12M, 3M, and 1M timeframes. Momentum tends to persist over the next 3-12 months, favouring ${w}.`
    },
    {
      metric: 'Quality Score', v1: s1.scores.quality, v2: s2.scores.quality, higherBetter: true,
      fmt: v => v + '/100',
      explain: (w,l) => `${w} scores higher on quality fundamentals — ROE, profit margins, and balance sheet strength. Higher quality companies historically command a return premium (RMW factor).`
    },
  ];

  const t1wins = rows.filter(r => winner(r.v1, r.v2, r.higherBetter) === t1).length;
  const t2wins = rows.filter(r => winner(r.v1, r.v2, r.higherBetter) === t2).length;
  const overall = t1wins > t2wins ? t1 : t2wins > t1wins ? t2 : 'Neither';
  const overallColor = overall === t1 ? '#22c55e' : overall === t2 ? '#3b82f6' : '#f59e0b';

  document.getElementById('compareTableWrap').innerHTML = `
    <div class="cmp-table-title">Head-to-Head Comparison</div>
    <div class="cmp-table-sub" style="margin-bottom:12px">
      <span style="color:#22c55e;font-weight:700">${t1}: ${t1wins} wins</span>
      &nbsp;·&nbsp;
      <span style="color:#3b82f6;font-weight:700">${t2}: ${t2wins} wins</span>
      &nbsp;·&nbsp;
      <span style="color:${overallColor};font-weight:700">Overall: ${overall} ${overall==='Neither'?'— evenly matched':'is the stronger pick'}</span>
    </div>
    <table class="cmp-table">
      <thead>
        <tr>
          <th>Metric</th>
          <th>${t1}</th>
          <th>${t2}</th>
          <th>Winner</th>
          <th>Why</th>
        </tr>
      </thead>
      <tbody>
        ${rows.map(r => {
          const w = winner(r.v1, r.v2, r.higherBetter);
          const l = w === t1 ? t2 : t1;
          const v1col = w === t1 ? '#22c55e' : w === t2 ? '#ef4444' : 'var(--text)';
          const v2col = w === t2 ? '#22c55e' : w === t1 ? '#ef4444' : 'var(--text)';
          return `<tr>
            <td style="font-weight:600;color:var(--text)">${r.metric}</td>
            <td style="font-family:var(--sans);font-weight:600;color:${v1col}">${r.fmt(r.v1)}</td>
            <td style="font-family:var(--sans);font-weight:600;color:${v2col}">${r.fmt(r.v2)}</td>
            <td>${winBadge(r.v1,r.v2,r.higherBetter)}</td>
            <td><div class="cmp-explain">${w!=='Tie'?r.explain(w,l):'Both stocks perform similarly on this metric.'}</div></td>
          </tr>`;
        }).join('')}
      </tbody>
    </table>`;
}

// ── Portfolio comparison table ────────────────────────────────────────────────
function renderPortCompareTable(left, right) {
  const m1 = left.metrics, m2 = right.metrics;
  const s1 = left.portfolio_score, s2 = right.portfolio_score;

  function winner(v1, v2, higherBetter=true) {
    if (higherBetter) return v1 > v2 ? 'A' : v2 > v1 ? 'B' : 'Tie';
    return v1 < v2 ? 'A' : v2 < v1 ? 'B' : 'Tie';
  }
  function winBadge(v1, v2, higherBetter=true) {
    const w = winner(v1, v2, higherBetter);
    if (w === 'Tie') return '<span style="font-size:10px;color:var(--muted)">Tie</span>';
    return `<span class="cmp-winner">Portfolio ${w} ✓</span>`;
  }

  const rows = [
    {metric:'Portfolio Score', v1:s1.composite, v2:s2.composite, higherBetter:true, fmt:v=>v+'/100',
     explain:(w,l)=>`Portfolio ${w} scores higher overall across risk-adjusted return, alpha generation, diversification, weight efficiency, and drawdown control.`},
    {metric:'Annualised Return', v1:m1.ann_return, v2:m2.ann_return, higherBetter:true, fmt:v=>pct(v),
     explain:(w,l)=>`Portfolio ${w} delivered ${pct(w==='A'?m1.ann_return:m2.ann_return)} vs ${pct(w==='A'?m2.ann_return:m1.ann_return)} for Portfolio ${l}.`},
    {metric:'Sharpe Ratio', v1:m1.sharpe, v2:m2.sharpe, higherBetter:true, fmt:v=>fix2(v),
     explain:(w,l)=>`Portfolio ${w} generates better risk-adjusted return (Sharpe ${fix2(w==='A'?m1.sharpe:m2.sharpe)} vs ${fix2(w==='A'?m2.sharpe:m1.sharpe)}).`},
    {metric:'Volatility', v1:m1.ann_vol, v2:m2.ann_vol, higherBetter:false, fmt:v=>pct(v),
     explain:(w,l)=>`Portfolio ${w} carries less total risk (${pct(w==='A'?m1.ann_vol:m2.ann_vol)} vs ${pct(w==='A'?m2.ann_vol:m1.ann_vol)}). Lower volatility means smoother drawdown profile.`},
    {metric:'Alpha', v1:m1.alpha, v2:m2.alpha, higherBetter:true, fmt:v=>pct(v),
     explain:(w,l)=>`Portfolio ${w} generates more return above its CAPM expectation, indicating better stock selection.`},
    {metric:'Max Drawdown', v1:m1.max_dd, v2:m2.max_dd, higherBetter:false, fmt:v=>'-'+(v*100).toFixed(2)+'%',
     explain:(w,l)=>`Portfolio ${w} experienced a shallower worst-case loss, requiring less recovery to break even.`},
    {metric:'Beta', v1:m1.beta, v2:m2.beta, higherBetter:false, fmt:v=>fix3(v),
     explain:(w,l)=>`Portfolio ${w} is less sensitive to market moves (beta ${fix3(w==='A'?m1.beta:m2.beta)}), offering more defensive characteristics.`},
    {metric:'Diversification', v1:s1.scores.diversification, v2:s2.scores.diversification, higherBetter:true, fmt:v=>v+'/100',
     explain:(w,l)=>`Portfolio ${w} has lower average cross-asset correlation (${w==='A'?s1.avg_correlation:s2.avg_correlation}), providing more genuine diversification benefit.`},
    {metric:'Weight Efficiency', v1:s1.scores.efficiency, v2:s2.scores.efficiency, higherBetter:true, fmt:v=>v+'/100',
     explain:(w,l)=>`Portfolio ${w}'s current weights are closer to the mathematically optimal max-Sharpe allocation.`},
  ];

  const aWins = rows.filter(r=>winner(r.v1,r.v2,r.higherBetter)==='A').length;
  const bWins = rows.filter(r=>winner(r.v1,r.v2,r.higherBetter)==='B').length;
  const overall = aWins > bWins ? 'A' : bWins > aWins ? 'B' : 'Neither';

  document.getElementById('compareTableWrap').innerHTML = `
    <div class="cmp-table-title">Portfolio Head-to-Head</div>
    <div class="cmp-table-sub" style="margin-bottom:12px">
      <span style="color:#22c55e;font-weight:700">Portfolio A: ${aWins} wins</span>
      &nbsp;·&nbsp;
      <span style="color:#3b82f6;font-weight:700">Portfolio B: ${bWins} wins</span>
      &nbsp;·&nbsp;
      <span style="color:${overall==='Neither'?'#f59e0b':overall==='A'?'#22c55e':'#3b82f6'};font-weight:700">
        ${overall==='Neither'?'Evenly matched':'Portfolio '+overall+' is better constructed'}
      </span>
    </div>
    <table class="cmp-table">
      <thead><tr><th>Metric</th><th>Portfolio A</th><th>Portfolio B</th><th>Winner</th><th>Why</th></tr></thead>
      <tbody>
        ${rows.map(r=>{
          const w=winner(r.v1,r.v2,r.higherBetter),l=w==='A'?'B':'A';
          const v1c=w==='A'?'#22c55e':w==='B'?'#ef4444':'var(--text)';
          const v2c=w==='B'?'#22c55e':w==='A'?'#ef4444':'var(--text)';
          return `<tr>
            <td style="font-weight:600;color:var(--text)">${r.metric}</td>
            <td style="font-weight:600;color:${v1c}">${r.fmt(r.v1)}</td>
            <td style="font-weight:600;color:${v2c}">${r.fmt(r.v2)}</td>
            <td>${winBadge(r.v1,r.v2,r.higherBetter)}</td>
            <td><div class="cmp-explain">${w!=='Tie'?r.explain(w,l):'Both portfolios perform similarly here.'}</div></td>
          </tr>`;
        }).join('')}
      </tbody>
    </table>`;
}"""

if "'use strict';" in content:
    content = content.replace("'use strict';", new)
    print('JS added: OK')
else:
    print('ERROR: use strict not found')

open('templates/index.html', 'w').write(content)
