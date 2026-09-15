content = open('templates/index.html').read()

old = """async function runAnalysis() {
  const ticker = document.getElementById('tickerInput').value.trim().toUpperCase();
  const period = document.getElementById('periodSelect').value;
  if (!ticker) return;

  const btn = document.getElementById('runBtn');
  btn.disabled = true;
  btn.textContent = 'Loading\u2026';
  setStatus('Fetching data\u2026');
  renderLoading();

  try {
    const res = await fetch('/api/analyse', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ticker, period })
    });
    const data = await res.json();
    if (data.error) throw new Error(data.error);

    state.ticker = ticker;
    state.period = period;
    state.data   = data;

    setStatus(`${ticker} \u00b7 ${period}`);
    if (currentModule === 'pricing')      renderPricing(data);
    else if (currentModule === 'factors') renderFactors(data);
    else if (currentModule === 'score')   renderScore(data);

  } catch (err) {
    renderError(err.message);
    setStatus('');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Analyse';
  }
}"""

new = """async function runAnalysis() {
  const ticker = document.getElementById('tickerInput').value.trim().toUpperCase();
  const period = document.getElementById('periodSelect').value;
  if (!ticker) return;

  const btn = document.getElementById('runBtn');
  btn.disabled = true;
  btn.textContent = 'Loading\u2026';
  setStatus('Fetching data\u2026');
  renderLoading();

  try {
    const res = await fetch('/api/analyse', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ticker, period })
    });
    const data = await res.json();
    if (data.error) throw new Error(data.error);

    state.ticker = ticker;
    state.period = period;
    state.pricing = data;
    state.factors = null;
    state.scoreData = null;

    setStatus(`${ticker} \u00b7 ${period}`);
    if (currentModule === 'pricing') renderPricing(data);
    else if (currentModule === 'factors') loadFactors();
    else if (currentModule === 'score') loadScore();

  } catch (err) {
    renderError(err.message);
    setStatus('');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Analyse';
  }
}

async function loadFactors() {
  if (!state.ticker) { renderEmpty(); return; }
  if (state.factors) { renderFactors(state.factors); return; }
  renderLoading();
  try {
    const res = await fetch('/api/factors', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ticker: state.ticker, period: state.period })
    });
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    state.factors = data;
    renderFactors(data);
  } catch(err) { renderError(err.message); }
}

async function loadScore() {
  if (!state.ticker) { renderEmpty(); return; }
  if (state.scoreData) { renderScore(state.scoreData); return; }
  renderLoading();
  try {
    const res = await fetch('/api/score', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ticker: state.ticker, period: state.period })
    });
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    state.scoreData = data;
    renderScore(data);
  } catch(err) { renderError(err.message); }
}"""

old2 = """  if (mod === 'portfolio') {
    panel.style.display = 'flex';
    content.style.display = 'none';
    if (!document.getElementById('portRows').children.length) {
      addPortRow(); addPortRow(); addPortRow();
    }
    if (state.portData) renderPortfolio(state.portData);
  } else {
    panel.style.display = 'none';
    content.style.display = 'block';
    if (!state.data) renderEmpty();
    else if (mod === 'pricing') renderPricing(state.data);
    else if (mod === 'factors') renderFactors(state.data);
    else if (mod === 'score')   renderScore(state.data);
  }"""

new2 = """  if (mod === 'portfolio') {
    panel.style.display = 'flex';
    content.style.display = 'none';
    if (!document.getElementById('portRows').children.length) {
      addPortRow(); addPortRow(); addPortRow();
    }
    if (state.portData) renderPortfolio(state.portData);
  } else {
    panel.style.display = 'none';
    content.style.display = 'block';
    if (mod === 'pricing') {
      if (!state.pricing) renderEmpty();
      else renderPricing(state.pricing);
    } else if (mod === 'factors') {
      loadFactors();
    } else if (mod === 'score') {
      loadScore();
    }
  }"""

result = content.replace(old, new)
result = result.replace(old2, new2)
open('templates/index.html', 'w').write(result)
print('Done')
