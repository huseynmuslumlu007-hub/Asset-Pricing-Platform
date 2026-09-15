content = open('templates/index.html').read()

old = """  Plotly.newPlot('chartFactors', [{
    x: labels, y: values, type: 'bar', orientation: 'v',
    marker: { color: values.map(v => v >= 0 ? 'rgba(34,197,94,0.7)' : 'rgba(239,68,68,0.7)') },
    text: values.map(v => v.toFixed(2) + '%'), textposition: 'outside'
  }], layout({
    yaxis: { ...PLOTLY_LAYOUT.yaxis, title: 'Contribution (%)' },
    showlegend: false
  }), { responsive: true, displayModeBar: false });

  // R2 comparison
  Plotly.newPlot('chartR2', [{
    x: ['FF3 Model', 'FF5 Model'],
    y: [+(ff3.r2 * 100).toFixed(2), +(ff5.r2 * 100).toFixed(2)],
    type: 'bar',
    marker: { color: ['#3b82f6', '#22c55e'] },
    text: [ff3.r2.toFixed(3), ff5.r2.toFixed(3)], textposition: 'outside'
  }], layout({
    yaxis: { ...PLOTLY_LAYOUT.yaxis, title: 'R\u00b2 (%)' },
    showlegend: false
  }), { responsive: true, displayModeBar: false });

  // Loadings radar-style bar
  const lKeys = Object.keys(ff5.loadings);
  const lVals = Object.values(ff5.loadings);
  Plotly.newPlot('chartLoadings', [{
    x: lKeys, y: lVals, type: 'bar',
    marker: { color: lVals.map(v => v >= 0 ? 'rgba(59,130,246,0.7)' : 'rgba(245,158,11,0.7)') }
  }], layout({ showlegend: false }), { responsive: true, displayModeBar: false });"""

new = """  Plotly.newPlot('chartFactors', [{
    x: labels, y: values, type: 'bar', orientation: 'v',
    marker: { color: values.map(v => v >= 0 ? 'rgba(34,197,94,0.7)' : 'rgba(239,68,68,0.7)') },
    text: values.map(v => v.toFixed(2) + '%'), textposition: 'outside'
  }], layout({
    xaxis: { ...PLOTLY_LAYOUT.xaxis, type: 'category' },
    yaxis: { ...PLOTLY_LAYOUT.yaxis, title: 'Contribution (%)' },
    showlegend: false
  }), { responsive: true, displayModeBar: false });

  // R2 comparison
  Plotly.newPlot('chartR2', [{
    x: ['FF3 Model', 'FF5 Model'],
    y: [+(ff3.r2 * 100).toFixed(2), +(ff5.r2 * 100).toFixed(2)],
    type: 'bar',
    marker: { color: ['#3b82f6', '#22c55e'] },
    text: [ff3.r2.toFixed(3), ff5.r2.toFixed(3)], textposition: 'outside'
  }], layout({
    xaxis: { ...PLOTLY_LAYOUT.xaxis, type: 'category' },
    yaxis: { ...PLOTLY_LAYOUT.yaxis, title: 'R\u00b2 (%)' },
    showlegend: false
  }), { responsive: true, displayModeBar: false });

  // Loadings bar
  const lKeys = Object.keys(ff5.loadings);
  const lVals = Object.values(ff5.loadings);
  Plotly.newPlot('chartLoadings', [{
    x: lKeys, y: lVals, type: 'bar',
    marker: { color: lVals.map(v => v >= 0 ? 'rgba(59,130,246,0.7)' : 'rgba(245,158,11,0.7)') }
  }], layout({
    xaxis: { ...PLOTLY_LAYOUT.xaxis, type: 'category' },
    showlegend: false
  }), { responsive: true, displayModeBar: false });"""

result = content.replace(old, new)
open('templates/index.html', 'w').write(result)
print('Done' if old in content else 'ERROR: pattern not found')
