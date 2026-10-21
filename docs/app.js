// Canlı demo: depodaki Python motoru (src/gpower_clone) Pyodide ile tarayıcıda çalışır.
// Bu dosya yalnızca arayüz yapıştırıcısıdır; hiçbir istatistik hesabı JavaScript'te yapılmaz.
'use strict';

const $ = (s, r = document) => r.querySelector(s);
const el = (tag, props = {}, ...kids) => {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (k === 'class') e.className = v; else if (k === 'text') e.textContent = v; else e.setAttribute(k, v);
  }
  for (const k of kids) e.append(k);
  return e;
};
const trNum = (s) => String(s ?? '').replace('.', ',');

const PY_FILES = ['__init__.py', 'contract.py', 'engine.py', 'display.py', 'cli.py'];
let py = null;
let runPy = null;

const GLUE = `
import json, math, time, os
import numpy as np
from scipy import stats
from gpower_clone.cli import evaluate
from gpower_clone.engine import calculate, GPowerError
from gpower_clone.display import format_result

def _plot(r):
    d1, d2, lam, crit = r.df1, r.df2, r.ncp, r.critical
    hi = stats.ncf.ppf(0.999, d1, d2, lam) if lam > 0 else stats.f.ppf(0.999, d1, d2)
    xmax = float(max(crit * 1.6, min(hi, crit * 12 + 40)))
    xs = np.linspace(xmax / 400, xmax, 400)
    h0 = stats.f.pdf(xs, d1, d2)
    h1 = stats.ncf.pdf(xs, d1, d2, lam) if lam > 0 else h0
    return {"x": xs.tolist(), "h0": np.nan_to_num(h0).tolist(), "h1": np.nan_to_num(h1).tolist(), "crit": float(crit)}

def run(params_json):
    p = json.loads(params_json)
    payload, warnings, code = evaluate(p)
    out = {"payload": payload, "warnings": list(warnings), "code": code}
    if code == 0:
        kw = dict(mode=p["mode"], f=p["f"], alpha=p["alpha"], groups=p["groups"])
        if p["mode"] == "a-priori": kw["power"] = p["power"]
        else: kw["total_n"] = p["total_n"]
        r = calculate(**kw)
        out["shown"] = format_result(r)
        out["plot"] = _plot(r)
    return json.dumps(out)

def verify_all():
    os.environ["ORACLE_DIR"] = "/home/pyodide/data"
    import helpers
    t0 = time.time()
    rows = helpers.read_csv("gpower_gui_vectors.csv")
    res = {row["id"]: helpers.compare_gui_row(row) for row in rows}
    return json.dumps({"n": len(rows), "results": res, "seconds": time.time() - t0})
`;

async function boot() {
  const status = $('#status');
  try {
    py = await loadPyodide({ indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/' });
    status.lastChild.textContent = 'scipy yükleniyor…';
    await py.loadPackage(['numpy', 'scipy']);
    py.FS.mkdirTree('/home/pyodide/gpower_clone');
    py.FS.mkdirTree('/home/pyodide/data');
    for (const f of PY_FILES) {
      const src = await (await fetch(`py/gpower_clone/${f}`)).text();
      py.FS.writeFile(`/home/pyodide/gpower_clone/${f}`, src);
    }
    py.FS.writeFile('/home/pyodide/helpers.py', await (await fetch('py/helpers.py')).text());
    py.FS.writeFile('/home/pyodide/data/gpower_gui_vectors.csv', await (await fetch('data/oracle.csv')).text());
    py.runPython("import sys; sys.path.insert(0, '/home/pyodide')");
    py.runPython(GLUE);
    runPy = py.globals.get('run');
    status.hidden = true;
    $('#verify').disabled = false;
    compute();
  } catch (err) {
    status.textContent = 'Python motoru yüklenemedi: ' + err.message + '. Sayfayı yenileyin; tablo ve kanıtlar yine de aşağıda.';
    console.error(err);
  }
}

function readForm() {
  const fd = new FormData($('#form'));
  const mode = fd.get('mode');
  const p = { mode, f: fd.get('f'), alpha: fd.get('alpha') };
  if (mode === 'a-priori') p.power = fd.get('power'); else p.total_n = fd.get('total_n');
  p.groups = fd.get('groups');
  for (const k of Object.keys(p)) if (k !== 'mode') p[k] = String(p[k]).replace(',', '.');
  return p;
}

function syncMode() {
  const mode = new FormData($('#form')).get('mode');
  document.querySelectorAll('[data-only]').forEach((n) => { n.hidden = n.dataset.only !== mode; });
}

function cliLine(p) {
  const flag = { f: '--f', alpha: '--alpha', power: '--power', total_n: '--n-total', groups: '--groups' };
  return '$ gpower-clone --test anova-oneway --mode ' + p.mode + ' ' +
    Object.entries(p).filter(([k]) => k !== 'mode').map(([k, v]) => `${flag[k]} ${v}`).join(' ');
}

function compute() {
  if (!runPy) return;
  const p = readForm();
  const out = JSON.parse(runPy(JSON.stringify(p)));
  $('#cmd').textContent = cliLine(p);
  $('#json').textContent = JSON.stringify(out.payload) + (out.code ? `   # çıkış kodu ${out.code}` : '');
  const err = $('#error');
  if (out.code !== 0) {
    $('#result').hidden = false;
    $('#headline').textContent = '';
    $('#plot').replaceChildren();
    $('#params').replaceChildren();
    $('#note').hidden = true;
    err.hidden = false;
    err.replaceChildren(el('b', { text: 'G*Power bu girdiyi reddeder' }), document.createTextNode(out.payload.error));
    return;
  }
  err.hidden = true;
  $('#result').hidden = false;
  const s = out.shown, pl = out.payload, k = Number(pl.df1) + 1;
  const h = $('#headline');
  if (p.mode === 'a-priori') {
    h.replaceChildren('Toplam ', el('b', { text: s.total_n }), ` hasta: her kolda ${trNum(pl.n_per_group)}.`);
  } else {
    h.replaceChildren('Güç ', el('b', { text: trNum(s.power) }), ` (N = ${s.total_n}, ${k} grup).`);
  }
  const rows = [
    ['Merkezi olmama parametresi λ', s.ncp], ['Kritik F', s.critical],
    ['Pay serbestlik derecesi', s.df1], ['Payda serbestlik derecesi', s.df2],
    ['Toplam örneklem', s.total_n], [p.mode === 'a-priori' ? 'Gerçekleşen güç' : 'Güç (1 − β)', s.power],
  ];
  $('#params').replaceChildren(...rows.map(([t, v]) => el('div', {}, el('dt', { text: t }), el('dd', { text: trNum(v) }))));
  const note = $('#note');
  note.hidden = !out.warnings.length;
  note.textContent = out.warnings.length ? 'G*Power uyarısı: ' + out.warnings.join(' ') : '';
  drawPlot(out.plot);
}

function drawPlot({ x, h0, h1, crit }) {
  const svg = $('#plot');
  const W = 640, H = 260, L = 36, R = 12, T = 14, B = 28;
  const xmax = x[x.length - 1];
  const peak1 = Math.max(...h1);
  const tail0 = Math.max(...h0.filter((_, i) => x[i] > crit * 0.5));
  const ymax = Math.max(peak1, tail0, 1e-9) * 1.18;
  const sx = (v) => L + (v / xmax) * (W - L - R);
  const sy = (v) => H - B - (v / ymax) * (H - T - B);
  const path = (ys, from = 0, to = x.length) => {
    let d = '';
    for (let i = from; i < to; i++) d += (d ? 'L' : 'M') + sx(x[i]).toFixed(1) + ' ' + sy(ys[i]).toFixed(1);
    return d;
  };
  const ci = x.findIndex((v) => v >= crit);
  const area = (ys, from, to) => {
    if (from >= to) return '';
    return path(ys, from, to) + `L${sx(x[to - 1]).toFixed(1)} ${sy(0)}L${sx(x[from]).toFixed(1)} ${sy(0)}Z`;
  };
  const ns = 'http://www.w3.org/2000/svg';
  const mk = (tag, attrs) => { const n = document.createElementNS(ns, tag); for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v); return n; };
  const kids = [];
  const defs = mk('defs', {}); const clip = mk('clipPath', { id: 'plot-clip' });
  clip.append(mk('rect', { x: L, y: T, width: W - L - R, height: H - T - B + 1 })); defs.append(clip); kids.push(defs);
  const g = mk('g', { 'clip-path': 'url(#plot-clip)' });
  const ticks = niceTicks(xmax);
  for (const t of ticks) {
    kids.push(mk('line', { x1: sx(t), x2: sx(t), y1: T, y2: H - B, stroke: 'var(--grid)' }));
    const lab = mk('text', { x: sx(t), y: H - 8, 'text-anchor': 'middle', 'font-size': 11, fill: 'var(--muted)' });
    lab.textContent = trNum(+t.toPrecision(3)); kids.push(lab);
  }
  kids.push(mk('line', { x1: L, x2: W - R, y1: H - B, y2: H - B, stroke: 'var(--muted)' }));
  if (ci > 0) {
    g.append(mk('path', { d: area(h1, 0, ci + 1), fill: 'var(--h1-wash)' }));
    g.append(mk('path', { d: area(h0, ci, x.length), fill: 'var(--h0-wash)' }));
  }
  g.append(mk('path', { d: path(h0), fill: 'none', stroke: 'var(--h0)', 'stroke-width': 2.2 }));
  g.append(mk('path', { d: path(h1), fill: 'none', stroke: 'var(--h1)', 'stroke-width': 2.2, 'stroke-dasharray': '7 5' }));
  kids.push(g);
  kids.push(mk('line', { x1: sx(crit), x2: sx(crit), y1: T, y2: H - B, stroke: 'var(--crit)', 'stroke-width': 2 }));
  const lab = mk('text', { x: Math.min(sx(crit) + 6, W - 120), y: T + 12, 'font-size': 12, fill: 'var(--crit)' });
  lab.textContent = 'kritik F = ' + trNum(crit.toPrecision(6)); kids.push(lab);
  const a = mk('text', { x: Math.min(sx(crit) + 10, W - 30), y: H - B - 10, 'font-size': 15, fill: 'var(--h0)', 'font-family': 'Spectral, serif' }); a.textContent = 'α';
  const b = mk('text', { x: Math.max(sx(crit) - 22, L + 4), y: H - B - 10, 'font-size': 15, fill: 'var(--h1)', 'font-family': 'Spectral, serif' }); b.textContent = 'β';
  kids.push(a, b);
  svg.replaceChildren(...kids);
  svg.setAttribute('aria-label', `F dağılımları; kritik F ${crit.toFixed(4)}`);
}

function niceTicks(max) {
  const raw = max / 6, p = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 2.5, 5, 10].map((m) => m * p).find((s) => s >= raw);
  const out = []; for (let t = 0; t <= max + 1e-9; t += step) out.push(t);
  return out;
}

// ------------------------------------------------------------- oracle table
let VECTORS = [];
const STATUS = { ok: ['ok', 'birebir'], known: ['known', 'G*Power sapıyor'], fail: ['fail', 'uyuşmuyor'] };
const FILTERS = [
  ['all', 'Tümü', () => true],
  ['result', 'Sonuçlu', (v) => v.kind !== 'error'],
  ['error', 'Hata mesajı', (v) => v.kind === 'error'],
  ['note', 'Uyarı', (v) => v.kind === 'note'],
  ['known', 'Bilinen sapma', (v) => v.status === 'known'],
];

async function loadVectors() {
  VECTORS = await (await fetch('data/vectors.json')).json();
  const bar = $('#filters');
  for (const [id, label, pred] of FILTERS) {
    const n = VECTORS.filter(pred).length;
    const btn = el('button', { type: 'button', 'aria-pressed': id === 'all' ? 'true' : 'false', 'data-f': id, text: `${label} (${n})` });
    btn.addEventListener('click', () => {
      bar.querySelectorAll('button').forEach((b) => b.setAttribute('aria-pressed', String(b === btn)));
      renderTable(pred);
    });
    bar.append(btn);
  }
  renderTable(() => true);
}

function cell(text, cls) { return el('td', cls ? { class: cls, text } : { text }); }

function renderTable(pred) {
  const body = $('#vectors tbody');
  body.replaceChildren(...VECTORS.filter(pred).map((v) => {
    const gp = v.kind === 'error' ? v.gp.message : v.gp.n;
    const mo = v.kind === 'error' ? v.motor.message : v.motor.n;
    const [cls, label] = STATUS[v.status];
    const tr = el('tr', { tabindex: '0' },
      cell(v.id), cell(v.mode === 'a-priori' ? 'a priori' : 'post hoc'), cell(trNum(v.f)), cell(trNum(v.alpha)),
      cell(trNum(v.mode === 'a-priori' ? v.power : v.n_total)), cell(trNum(v.groups)),
      cell(gp, v.kind === 'error' ? 'msg' : 'num'), cell(mo, v.kind === 'error' ? 'msg' : 'num'),
      el('td', {}, el('span', { class: 'badge ' + cls, 'data-id': v.id, text: label })));
    const open = () => openShot(v);
    tr.addEventListener('click', open);
    tr.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
    return tr;
  }));
}

function openShot(v) {
  $('#shot-title').textContent = `${v.id} · ${v.why}`;
  const img = $('#shot-img');
  img.src = v.shot; img.alt = `${v.id} için G*Power 3.1.9.7 penceresi`;
  const rows = [['Alan', 'G*Power', 'Bu motor']];
  const names = { n: 'Toplam N', power: 'Güç', critical: 'Kritik F', df1: 'df1', df2: 'df2', ncp: 'λ' };
  if (v.kind !== 'error') for (const [k, t] of Object.entries(names)) rows.push([t, v.gp[k], v.motor[k]]);
  const box = $('#shot-compare');
  box.replaceChildren();
  rows.forEach((r, i) => r.forEach((c) => {
    const differs = i > 0 && r[1] !== r[2];
    box.append(el(i === 0 ? 'p' : 'p', { class: i === 0 ? 'h' : (differs ? 'diff' : ''), text: trNum(c) }));
  }));
  if (v.gp.message) box.append(el('p', { class: 'wide', text: 'G*Power mesajı: ' + v.gp.message }));
  if (v.motor.message) box.append(el('p', { class: 'wide', text: 'Motorun mesajı: ' + v.motor.message }));
  if (v.status === 'known') box.append(el('p', { class: 'wide diff', text: 'Bilinen sayısal sapma: G*Power çok büyük payda serbestlik derecesinde kayıyor; motorun değeri 40 basamaklı bağımsız hesapla doğrulandı.' }));
  $('#shot').showModal();
}

async function verifyAll() {
  const btn = $('#verify'), out = $('#verify-out');
  btn.disabled = true; out.textContent = '63 vektör tarayıcıda yeniden hesaplanıyor…';
  await new Promise((r) => setTimeout(r, 30));
  const res = JSON.parse(py.globals.get('verify_all')());
  const known = new Set(VECTORS.filter((v) => v.status === 'known').map((v) => v.id));
  let ok = 0, dev = 0, bad = 0;
  for (const [id, diffs] of Object.entries(res.results)) {
    if (!diffs.length) ok++; else if (known.has(id)) dev++; else bad++;
  }
  out.replaceChildren('Tarayıcınızda, diferansiyel testin aynı karşılaştırma koduyla: ',
    el('b', { text: `${ok} / ${res.n} birebir` }), `, ${dev} bilinen sapma, ${bad} açıklanmamış uyuşmazlık · ${res.seconds.toFixed(1)} sn`);
  btn.disabled = false;
}

// ------------------------------------------------------------- wiring
let timer;
$('#form').addEventListener('input', () => { syncMode(); clearTimeout(timer); timer = setTimeout(compute, 180); });
$('#form').addEventListener('submit', (e) => e.preventDefault());
document.querySelectorAll('[data-preset]').forEach((b) => b.addEventListener('click', () => {
  const p = JSON.parse(b.dataset.preset);
  const form = $('#form');
  form.querySelector(`[name=mode][value=${p.mode}]`).checked = true;
  for (const [k, v] of Object.entries(p)) if (k !== 'mode') form.elements[k].value = v;
  syncMode(); compute();
}));
$('#verify').addEventListener('click', verifyAll);
syncMode();
loadVectors();
boot();
