content = open('templates/index.html').read()

# 1. Add nav item
old_nav = """      <div class="nav-item" id="nav-score" onclick="switchModule('score')">
        <svg class="nav-icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><polygon points="8,1 10,6 15,6 11,9 13,14 8,11 3,14 5,9 1,6 6,6"/></svg>
        Investment Score
      </div>"""

new_nav = """      <div class="nav-item" id="nav-score" onclick="switchModule('score')">
        <svg class="nav-icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><polygon points="8,1 10,6 15,6 11,9 13,14 8,11 3,14 5,9 1,6 6,6"/></svg>
        Investment Score
      </div>
      <div class="nav-item" id="nav-compare" onclick="switchModule('compare')">
        <svg class="nav-icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M1 8h14M8 1v14"/></svg>
        Compare
      </div>"""

if old_nav in content:
    content = content.replace(old_nav, new_nav)
    print('nav item: OK')
else:
    print('nav item: ERROR')

# 2. Add compare panel HTML before closing </div></div>
old_shell_end = """<!-- Two-panel Modal -->"""

new_shell_end = """<!-- Compare Panel -->
<div class="compare-panel" id="comparePanel" style="display:none">
  <div class="compare-topbar">
    <div class="compare-mode-toggle">
      <button class="mode-btn active" id="modeStocks" onclick="setCompareMode('stocks')">Stock Comparison</button>
      <button class="mode-btn" id="modePortfolios" onclick="setCompareMode('portfolios')">Portfolio Comparison</button>
    </div>
    <select id="comparePeriod" class="topbar-sel">
      <option value="1y">1 Year</option>
      <option value="2y" selected>2 Years</option>
      <option value="3y">3 Years</option>
      <option value="5y">5 Years</option>
    </select>
    <button class="compare-run-btn" id="compareRunBtn" onclick="runCompare()">Run Comparison</button>
  </div>
  <div class="compare-inputs" id="compareInputs">
    <!-- filled by setCompareMode -->
  </div>
  <div class="compare-results" id="compareResults" style="display:none">
    <div class="compare-side" id="compareLeft"></div>
    <div class="compare-side" id="compareRight"></div>
    <div class="compare-table-wrap" id="compareTableWrap"></div>
  </div>
</div>

<!-- Two-panel Modal -->"""

if old_shell_end in content:
    content = content.replace(old_shell_end, new_shell_end)
    print('compare panel HTML: OK')
else:
    print('compare panel HTML: ERROR')

# 3. Add CSS
old_css_end = """@media(max-width:900px){.charts-2col{grid-template-columns:1fr}.opt-grid{grid-template-columns:1fr}.score-row{grid-template-columns:140px 1fr 40px}.modal-inner{grid-template-columns:1fr}}
@media(max-width:640px){.sidebar{display:none}.metrics-grid{grid-template-columns:repeat(2,1fr)}}"""

new_css_end = """@media(max-width:900px){.charts-2col{grid-template-columns:1fr}.opt-grid{grid-template-columns:1fr}.score-row{grid-template-columns:140px 1fr 40px}.modal-inner{grid-template-columns:1fr}}
@media(max-width:640px){.sidebar{display:none}.metrics-grid{grid-template-columns:repeat(2,1fr)}}

/* ── Compare module ── */
.compare-panel{flex:1;overflow-y:auto;display:flex;flex-direction:column}
.compare-topbar{padding:14px 24px;background:var(--surface);border-bottom:1px solid var(--border);display:flex;align-items:center;gap:12px;flex-shrink:0}
.compare-mode-toggle{display:flex;background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:3px;gap:3px}
.mode-btn{background:none;border:none;color:var(--muted);font-size:13px;font-weight:500;padding:6px 14px;border-radius:6px;cursor:pointer;font-family:var(--sans);transition:all 0.15s}
.mode-btn.active{background:var(--accent);color:#111;font-weight:600}
.topbar-sel{background:rgba(255,255,255,0.04);border:1px solid var(--border-strong);border-radius:8px;padding:7px 10px;color:var(--text);font-size:12px;font-family:var(--sans);outline:none}
.compare-run-btn{background:var(--accent);color:#111;border:none;border-radius:8px;padding:8px 20px;font-size:13px;font-weight:600;cursor:pointer;font-family:var(--sans);transition:filter 0.15s,transform 0.15s;margin-left:auto}
.compare-run-btn:hover{filter:brightness(1.12);transform:translateY(-1px)}
.compare-run-btn:disabled{background:var(--border-strong);color:var(--muted);cursor:not-allowed;filter:none;transform:none}
.compare-inputs{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--border);flex-shrink:0}
.compare-input-side{background:var(--bg);padding:20px 24px}
.compare-input-label{font-size:11px;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:12px}
.compare-ticker-input{width:100%;background:rgba(255,255,255,0.04);border:1px solid var(--border-strong);border-radius:8px;padding:10px 14px;color:var(--text);font-family:var(--sans);font-size:15px;font-weight:600;outline:none;text-transform:uppercase;transition:border-color 0.15s,box-shadow 0.15s;letter-spacing:0.05em}
.compare-ticker-input:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(209,213,219,0.15)}
.compare-ticker-input::placeholder{color:var(--muted);text-transform:none;font-weight:400;letter-spacing:0;font-size:13px}
.compare-results{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--border);flex:1}
.compare-side{background:var(--bg);padding:24px;overflow-y:auto}
.compare-table-wrap{grid-column:1/-1;background:var(--bg);padding:24px;border-top:1px solid var(--border)}
.compare-side-title{font-size:13px;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:16px;padding-bottom:10px;border-bottom:1px solid var(--border)}
.cmp-metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:20px}
.cmp-score-row{display:flex;align-items:center;gap:20px;margin-bottom:20px}
/* Comparison table */
.cmp-table{width:100%;border-collapse:collapse;font-size:13px}
.cmp-table-title{font-size:16px;font-weight:700;margin-bottom:4px}
.cmp-table-sub{font-size:12px;color:var(--muted);margin-bottom:16px}
.cmp-table th{padding:10px 14px;text-align:left;font-size:10px;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.8px;border-bottom:1px solid var(--border);background:rgba(255,255,255,0.02)}
.cmp-table td{padding:10px 14px;border-bottom:1px solid var(--border);vertical-align:top}
.cmp-table tr:hover td{background:rgba(255,255,255,0.03)}
.cmp-winner{display:inline-block;font-size:10px;font-weight:700;padding:2px 8px;border-radius:20px;background:rgba(34,197,94,0.15);color:#22c55e;margin-left:6px}
.cmp-explain{font-size:11px;color:var(--muted);margin-top:3px;line-height:1.5}
/* Port compare inputs */
.port-compare-rows{display:flex;flex-direction:column;gap:6px;margin-top:8px}"""

if old_css_end in content:
    content = content.replace(old_css_end, new_css_end)
    print('CSS: OK')
else:
    print('CSS: ERROR')

open('templates/index.html', 'w').write(content)
