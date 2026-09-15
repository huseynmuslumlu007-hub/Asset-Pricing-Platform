content = open('templates/index.html').read()

old = """  Plotly.newPlot('chartEF', [{
    x: ef.vols.map(v => v * 100), y: ef.returns.map(v => v * 100),
    mode: 'markers', type: 'scatter', name: 'Portfolios',
    marker: { color: ef.sharpes, colorscale: 'Viridis', size: 4, showscale: true,
              colorbar: { title: 'Sharpe', thickness: 12, len: 0.8 } }
  }], layout({
    xaxis: { ...PLOTLY_LAYOUT.xaxis, title: 'Volatility (%)' },
    yaxis: { ...PLOTLY_LAYOUT.yaxis, title: 'Return (%)' },
    hovermode: 'closest'
  }), { responsive: true, displayModeBar: false });"""

new = """  Plotly.newPlot('chartEF', [{
    x: ef.vols.map(v => v * 100), y: ef.returns.map(v => v * 100),
    mode: 'markers', type: 'scatter', name: 'Portfolios',
    marker: { color: ef.sharpes, colorscale: 'Viridis', size: 4, showscale: true,
              colorbar: { title: 'Sharpe', thickness: 12, len: 0.8 } }
  }], layout({
    xaxis: { ...PLOTLY_LAYOUT.xaxis, title: 'Volatility (%)', type: 'linear' },
    yaxis: { ...PLOTLY_LAYOUT.yaxis, title: 'Return (%)', type: 'linear' },
    hovermode: 'closest'
  }), { responsive: true, displayModeBar: false });"""

old2 = """  Plotly.newPlot('chartCorr', [{
    z: corr.values, x: corr.labels, y: corr.labels,
    type: 'heatmap', colorscale: 'RdBu', reversescale: true, zmin: -1, zmax: 1
  }], layout({ margin: { t: 10, r: 10, b: 60, l: 60 } }), { responsive: true, displayModeBar: false });"""

new2 = """  Plotly.newPlot('chartCorr', [{
    z: corr.values, x: corr.labels, y: corr.labels,
    type: 'heatmap', colorscale: 'RdBu', reversescale: true, zmin: -1, zmax: 1
  }], layout({
    margin: { t: 10, r: 10, b: 60, l: 60 },
    xaxis: { ...PLOTLY_LAYOUT.xaxis, type: 'category' },
    yaxis: { ...PLOTLY_LAYOUT.yaxis, type: 'category' }
  }), { responsive: true, displayModeBar: false });"""

result = content.replace(old, new).replace(old2, new2)
open('templates/index.html', 'w').write(result)
print('EF fix:', old in content)
print('Corr fix:', old2 in content)
