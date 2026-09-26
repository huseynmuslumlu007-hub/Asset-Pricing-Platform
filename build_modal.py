content = open('templates/index.html').read()

# Replace simple modal CSS and HTML with full two-panel system
old_css = """/* ── Modal overlay ── */
.modal-overlay{position:fixed;inset:0;z-index:1000;background:rgba(0,0,0,0.88);backdrop-filter:blur(8px);display:flex;align-items:center;justify-content:center;opacity:0;transition:opacity 0.25s ease;pointer-events:none}
.modal-overlay.open{opacity:1;pointer-events:all}
.modal-box{background:var(--surface);border:1px solid var(--border-strong);border-top:2px solid var(--accent);border-radius:var(--radius);padding:28px;max-width:700px;width:92%;max-height:88vh;overflow-y:auto;box-shadow:0 20px 60px rgba(0,0,0,0.6);position:relative}
.modal-close{position:absolute;top:16px;right:16px;background:none;border:none;color:var(--muted);font-size:22px;cursor:pointer;line-height:1;transition:color 0.15s}
.modal-close:hover{color:var(--text)}
.modal-title{font-size:16px;font-weight:700;margin-bottom:4px}
.modal-sub{font-size:12px;color:var(--muted);margin-bottom:20px}
.explain-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.explain-card{background:var(--border);border-radius:10px;padding:16px;cursor:default;transition:transform 0.18s ease,box-shadow 0.18s ease}
.explain-card:hover{transform:translateY(-3px);box-shadow:0 8px 32px rgba(0,0,0,0.6),0 0 0 1px rgba(255,255,255,0.15)}
.explain-card-label{font-size:10px;text-transform:uppercase;color:var(--text-muted);letter-spacing:0.8px;margin-bottom:4px;font-weight:700}
.explain-card-value{font-size:18px;font-weight:700;font-family:var(--mono);margin-bottom:6px}
.explain-card-text{font-size:12px;color:var(--muted);line-height:1.6}"""

new_css = """/* ── Two-panel modal ── */
.modal-overlay{position:fixed;inset:0;z-index:1000;background:rgba(0,0,0,0.88);backdrop-filter:blur(8px);display:flex;align-items:center;justify-content:center;opacity:0;transition:opacity 0.25s ease;pointer-events:none;padding:20px}
.modal-overlay.open{opacity:1;pointer-events:all}
.modal-inner{display:grid;grid-template-columns:1fr 360px;gap:16px;width:100%;max-width:1300px;max-height:92vh}
.modal-left{background:var(--surface);border:1px solid var(--border-strong);border-top:2px solid var(--accent);border-radius:var(--radius);padding:28px;overflow-y:auto;max-height:92vh;position:relative;box-shadow:0 20px 60px rgba(0,0,0,0.6)}
.modal-right{background:var(--surface);border:1px solid var(--border-strong);border-top:2px solid var(--accent);border-radius:var(--radius);padding:24px;overflow-y:auto;max-height:92vh;box-shadow:0 20px 60px rgba(0,0,0,0.6)}
.modal-close{position:absolute;top:16px;right:16px;background:none;border:1px solid var(--border-strong);border-radius:6px;color:var(--muted);font-size:13px;cursor:pointer;padding:4px 10px;transition:color 0.15s,border-color 0.15s;z-index:10}
.modal-close:hover{color:var(--text);border-color:var(--accent)}
.modal-left-title{font-size:11px;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:16px}
.modal-chart-area{height:320px}
.modal-right-label{font-size:10px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:16px}
.explain-card{background:#1a2030;border:1px solid var(--border-strong);border-top:2px solid var(--accent);border-radius:12px;padding:20px;margin-bottom:12px;cursor:pointer;transition:transform 0.18s ease,box-shadow 0.18s ease;opacity:0;animation:cardIn 0.3s ease forwards}
.explain-card:hover{transform:translateY(-3px);box-shadow:0 8px 32px rgba(0,0,0,0.5),0 0 0 1px rgba(255,255,255,0.3)}
.explain-card-label{font-size:12px;text-transform:uppercase;color:#64748b;letter-spacing:0.8px;margin-bottom:8px;font-weight:700}
.explain-card-value{font-size:20px;font-weight:700;font-family:var(--mono);margin-bottom:10px}
.explain-card-text{font-size:14px;color:#94a3b8;line-height:1.8}
/* second popup */
.card-popup{position:fixed;inset:0;z-index:1100;background:rgba(0,0,0,0.92);backdrop-filter:blur(12px);display:flex;align-items:center;justify-content:center;opacity:0;transition:opacity 0.2s ease;pointer-events:none;padding:40px}
.card-popup.open{opacity:1;pointer-events:all}
.card-popup-box{background:#1a2030;border:1px solid var(--border-strong);border-top:2px solid var(--accent);border-radius:var(--radius);padding:52px;max-width:640px;width:100%;box-shadow:0 20px 60px rgba(0,0,0,0.8)}
.card-popup-label{font-size:12px;text-transform:uppercase;color:#64748b;letter-spacing:1px;margin-bottom:12px;font-weight:700}
.card-popup-value{font-size:32px;font-weight:700;font-family:var(--mono);margin-bottom:16px}
.card-popup-text{font-size:18px;color:#94a3b8;line-height:1.8}"""

# Replace modal HTML
old_html = """<!-- ── Modal ── -->
<div class="modal-overlay" id="modalOverlay" onclick="closeModal(event)">
  <div class="modal-box" id="modalBox">
    <button class="modal-close" onclick="closeModalDirect()">✕</button>
    <div class="modal-title" id="modalTitle"></div>
    <div class="modal-sub" id="modalSub"></div>
    <div class="explain-grid" id="modalGrid"></div>
  </div>
</div>"""

new_html = """<!-- ── Two-panel Modal ── -->
<div class="modal-overlay" id="modalOverlay" onclick="closeModal(event)">
  <div class="modal-inner">
    <div class="modal-left" id="modalLeft">
      <button class="modal-close" onclick="closeModalDirect()">✕ Close</button>
      <div class="modal-left-title" id="modalLeftTitle"></div>
      <div id="modalLeftContent"></div>
    </div>
    <div class="modal-right" id="modalRight">
      <div class="modal-right-label">Explanation</div>
      <div id="modalCards"></div>
    </div>
  </div>
</div>
<!-- ── Card popup ── -->
<div class="card-popup" id="cardPopup" onclick="closeCardPopup(event)">
  <div class="card-popup-box" id="cardPopupBox">
    <div class="card-popup-label" id="cardPopupLabel"></div>
    <div class="card-popup-value" id="cardPopupValue"></div>
    <div class="card-popup-text" id="cardPopupText"></div>
  </div>
</div>"""

# Replace modal JS functions
old_js = """// ─────────────────────────────────────────────
//  Modal
// ─────────────────────────────────────────────
function openModal(title, sub, cards) {
  document.getElementById('modalTitle').textContent = title;
  document.getElementById('modalSub').textContent = sub;
  const grid = document.getElementById('modalGrid');
  grid.innerHTML = cards.map((c, i) => `
    <div class="explain-card" style="animation:cardIn 0.3s ease ${i * 0.08}s both">
      <div class="explain-card-label">${c.label}</div>
      <div class="explain-card-value" style="color:${c.color || 'var(--accent)'}">${c.value}</div>
      <div class="explain-card-text">${c.text}</div>
    </div>`).join('');
  document.getElementById('modalOverlay').classList.add('open');
}

function closeModal(e) {
  if (e.target === document.getElementById('modalOverlay')) closeModalDirect();
}
function closeModalDirect() {
  document.getElementById('modalOverlay').classList.remove('open');
}
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModalDirect(); });"""

new_js = """// ─────────────────────────────────────────────
//  Two-panel Modal
// ─────────────────────────────────────────────
let _currentModalChartId = null;

function openModal(leftTitle, leftContentHTML, cards, chartRenderer) {
  document.getElementById('modalLeftTitle').textContent = leftTitle;
  document.getElementById('modalLeftContent').innerHTML = leftContentHTML;

  const cardContainer = document.getElementById('modalCards');
  cardContainer.innerHTML = cards.map((c, i) => `
    <div class="explain-card" style="animation-delay:${i * 0.13}s" onclick="openCardPopup('${encodeURIComponent(c.label)}','${encodeURIComponent(c.value)}','${encodeURIComponent(c.text)}','${c.color||'#d1d5db'}')">
      <div class="explain-card-label">${c.label}</div>
      <div class="explain-card-value" style="color:${c.color||'#d1d5db'}">${c.value}</div>
      <div class="explain-card-text">${c.text}</div>
    </div>`).join('');

  document.getElementById('modalOverlay').classList.add('open');

  if (chartRenderer) {
    setTimeout(() => chartRenderer(), 80);
  }
}

function openCardPopup(label, value, text, color) {
  document.getElementById('cardPopupLabel').textContent = decodeURIComponent(label);
  document.getElementById('cardPopupValue').textContent = decodeURIComponent(value);
  document.getElementById('cardPopupValue').style.color = color;
  document.getElementById('cardPopupText').textContent = decodeURIComponent(text);
  document.getElementById('cardPopup').classList.add('open');
}

function closeCardPopup(e) {
  if (e.target === document.getElementById('cardPopup')) {
    document.getElementById('cardPopup').classList.remove('open');
  }
}

function closeModal(e) {
  if (e.target === document.getElementById('modalOverlay')) closeModalDirect();
}

function closeModalDirect() {
  document.getElementById('modalOverlay').classList.remove('open');
  document.getElementById('cardPopup').classList.remove('open');
}

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    if (document.getElementById('cardPopup').classList.contains('open')) {
      document.getElementById('cardPopup').classList.remove('open');
    } else {
      closeModalDirect();
    }
  }
});

// ─── Open metric modal (left = big metric card, right = explanation cards) ───
function openMetricModal(leftTitle, leftHTML, cards) {
  openModal(leftTitle, leftHTML, cards, null);
}

// ─── Open chart modal (left = re-rendered chart, right = explanation cards) ──
function openChartModal(leftTitle, chartHTML, cards, chartRenderer) {
  openModal(leftTitle, chartHTML, cards, chartRenderer);
}"""

fixes = [
    (old_css, new_css, 'Modal CSS'),
    (old_html, new_html, 'Modal HTML'),
    (old_js, new_js, 'Modal JS'),
]

result = content
for old, new, name in fixes:
    if old in result:
        result = result.replace(old, new)
        print(f'{name}: OK')
    else:
        print(f'{name}: ERROR not found')

open('templates/index.html', 'w').write(result)
