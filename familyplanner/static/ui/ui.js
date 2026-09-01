/* Family Success Planner - preview UI.
   State lives in one object; every change re-renders the affected controls and
   asks the server for a fresh preview of the current page. */

const $ = (sel) => document.querySelector(sel);
const el = (tag, cls) => { const n = document.createElement(tag); if (cls) n.className = cls; return n; };

const MEMBER_DOTS = ["#14A0A5", "#EF3E63", "#F7A81B", "#6DB033", "#7C4DA0", "#2F6FD1"];

const state = {
  year: 2027, family_name: "", week_starts: "sunday", dated_months: true,
  page_size: "letter", members: [], pages: [], theme: "classic", fonts: "classic",
  preview: null, zoom: null,
};
let meta = { themes: [], typefaces: [], catalogue: [], months: [], defaultPages: [] };
let previewSeq = 0;

/* --- helpers -------------------------------------------------------------- */

function toast(message, kind = "", code = "") {
  const node = $("#toast");
  node.textContent = message;
  if (code) {
    const c = el("code");
    c.textContent = code;
    node.append(" ", c);
  }
  node.dataset.kind = kind;
  node.dataset.show = "1";
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => { node.dataset.show = "0"; }, kind === "error" ? 7000 : 4200);
}

async function api(path, body) {
  const res = await fetch(path, {
    method: body ? "POST" : "GET",
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({ error: "malformed response" }));
  if (!res.ok || data.error) throw new Error(data.error || `request failed (${res.status})`);
  return data;
}

/* The ordered list of pages currently in the book, months expanded. */
function bookPages() {
  const titles = new Map(meta.catalogue.map((p) => [p.slug, p.title]));
  const out = [];
  for (const slug of state.pages) {
    if (slug === "months") {
      for (const m of meta.months) out.push({ slug: m.toLowerCase(), title: `${m} Family Planner` });
    } else if (titles.has(slug)) {
      out.push({ slug, title: titles.get(slug) });
    }
  }
  return out;
}

/* --- rendering the controls ---------------------------------------------- */

function renderThemes() {
  const host = $("#themes");
  host.textContent = "";
  for (const theme of meta.themes) {
    const label = el("label", "swatch");
    label.dataset.on = state.theme === theme.name ? "1" : "0";
    const chips = el("div", "swatch-chips");
    for (const colour of theme.swatches) {
      const i = el("i");
      i.style.background = colour;
      chips.append(i);
    }
    const input = el("input");
    Object.assign(input, { type: "radio", name: "theme", value: theme.name,
                           checked: state.theme === theme.name });
    input.addEventListener("change", () => { state.theme = theme.name; renderThemes(); refresh(); });
    const name = el("span", "swatch-name");
    name.textContent = theme.name;
    label.append(input, chips, name);
    host.append(label);
  }
}

/* A config may name three families instead of a preset. That choice has to be
   visible and selectable, or opening the UI would silently discard it. */
function customFonts() {
  return typeof state.fonts === "object" && state.fonts !== null ? state.fonts : null;
}

function fontsEqual(a, b) {
  if (typeof a !== typeof b) return false;
  if (typeof a === "string") return a === b;
  return a && b && a.display === b.display && a.script === b.script && a.body === b.body;
}

function renderTypefaces() {
  const host = $("#typefaces");
  host.textContent = "";

  const custom = customFonts();
  const sets = custom
    ? [{ name: "custom", ...custom }, ...meta.typefaces]
    : meta.typefaces;

  for (const set of sets) {
    const isCustom = set.name === "custom";
    const value = isCustom ? { display: set.display, script: set.script, body: set.body } : set.name;
    const selected = fontsEqual(state.fonts, value);

    const label = el("label", "type-card");
    label.dataset.on = selected ? "1" : "0";
    if (isCustom) label.title = "From your config file";
    const input = el("input");
    Object.assign(input, { type: "radio", name: "fonts", checked: selected });
    input.addEventListener("change", () => { state.fonts = value; renderTypefaces(); refresh(); });
    const name = el("span", "type-name");
    name.textContent = set.name;
    const spec = el("span", "type-spec");
    const b = el("b");
    b.textContent = set.display;
    spec.append(b, document.createTextNode(`${set.script} · ${set.body}`));
    label.append(input, name, spec);
    host.append(label);
  }
}

function renderMembers() {
  const host = $("#members");
  host.textContent = "";
  state.members.forEach((value, index) => {
    const row = el("div", "member");
    const dot = el("span", "dot");
    dot.style.background = MEMBER_DOTS[index % MEMBER_DOTS.length];
    const input = el("input");
    Object.assign(input, { type: "text", value, placeholder: `Person ${index + 1}` });
    input.setAttribute("aria-label", `Tracker row ${index + 1}`);
    input.addEventListener("input", () => { state.members[index] = input.value; });
    input.addEventListener("change", refresh);
    const remove = el("button");
    remove.type = "button";
    remove.textContent = "×";
    remove.setAttribute("aria-label", `Remove row ${index + 1}`);
    remove.addEventListener("click", () => {
      state.members.splice(index, 1); renderMembers(); refresh();
    });
    row.append(dot, input, remove);
    host.append(row);
  });
}

function renderPages() {
  const host = $("#pages");
  host.textContent = "";
  const rows = [...meta.defaultPages];
  for (const p of meta.catalogue) if (!rows.includes(p.slug)) rows.push(p.slug);

  const titles = new Map(meta.catalogue.map((p) => [p.slug, p.title]));
  for (const slug of rows) {
    const isMonths = slug === "months";
    const title = isMonths ? "Monthly planners (12)" : titles.get(slug);
    if (!title) continue;

    const row = el("div", "page-row");
    const on = state.pages.includes(slug);
    row.dataset.slug = slug;
    row.dataset.current = pageRowIsCurrent(slug) ? "1" : "0";
    row.tabIndex = 0;
    row.setAttribute("role", "button");
    row.setAttribute("aria-pressed", pageRowIsCurrent(slug) ? "true" : "false");
    row.title = `Preview ${title}`;

    const input = el("input");
    Object.assign(input, { type: "checkbox", checked: on });
    input.setAttribute("aria-label", `Include ${title}`);
    input.addEventListener("click", (event) => event.stopPropagation());
    input.addEventListener("change", () => {
      if (input.checked) {
        const order = rows.filter((s) => s === slug || state.pages.includes(s));
        state.pages = order;
      } else {
        state.pages = state.pages.filter((s) => s !== slug);
      }
      syncPreviewChoices();
      markCurrentPage();
      refresh();
    });

    const box = el("span", "box");
    const check = el("label", "page-check");
    check.addEventListener("click", (event) => event.stopPropagation());
    check.append(input, box);

    const label = el("span", "title");
    label.textContent = title;

    row.addEventListener("click", () => showPage(slug, isMonths));
    row.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        showPage(slug, isMonths);
      }
    });

    row.append(check, label);
    host.append(row);
  }
}

function pageRowIsCurrent(slug) {
  if (slug === "months") {
    return meta.months.some((name) => name.toLowerCase() === state.preview);
  }
  return slug === state.preview;
}

function showPage(slug, isMonths) {
  state.preview = isMonths ? (meta.months[0] || "").toLowerCase() : slug;
  syncPreviewChoices();
  markCurrentPage();
  refresh();
}

function markCurrentPage() {
  for (const row of document.querySelectorAll(".page-row")) {
    const on = pageRowIsCurrent(row.dataset.slug);
    row.dataset.current = on ? "1" : "0";
    row.setAttribute("aria-pressed", on ? "true" : "false");
  }
}

function syncPreviewChoices() {
  const select = $("#preview-page");
  const pages = bookPages();
  if (!pages.some((p) => p.slug === state.preview)) state.preview = pages[0]?.slug || null;
  select.textContent = "";
  pages.forEach((page, index) => {
    const option = el("option");
    option.value = page.slug;
    option.textContent = `${String(index + 1).padStart(2, "0")}  ${page.title}`;
    option.selected = page.slug === state.preview;
    select.append(option);
  });
  $("#brand-sub").textContent = `${pages.length} page${pages.length === 1 ? "" : "s"} · ${state.page_size}`;
}

/* --- preview -------------------------------------------------------------- */

let refreshTimer = null;
function refresh() {
  clearTimeout(refreshTimer);
  refreshTimer = setTimeout(loadPreview, 160);   // coalesce rapid edits
}

async function loadPreview() {
  const seq = ++previewSeq;
  $("#spinner").hidden = false;
  try {
    const data = await api("/api/preview", { ...state });
    if (seq !== previewSeq) return;              // a newer request won
    $("#preview").srcdoc = data.html;
    requestAnimationFrame(applyZoom);
  } catch (error) {
    if (seq === previewSeq) toast(error.message, "error");
  } finally {
    if (seq === previewSeq) $("#spinner").hidden = true;
  }
}

/* Page size in CSS pixels at 96dpi, so the sheet matches the paper choice. */
function sheetSize() {
  return state.page_size === "a4" ? [794, 1123] : [816, 1056];
}

function applyZoom() {
  const [w, h] = sheetSize();
  const sheet = $("#sheet");
  sheet.style.width = `${w}px`;
  sheet.style.height = `${h}px`;

  const canvas = $("#canvas");
  const fit = Math.min((canvas.clientWidth - 52) / w, (canvas.clientHeight - 52) / h);
  const scale = state.zoom || fit;
  sheet.style.transform = `scale(${scale})`;
  // Reserve the scaled footprint so the scroll area matches what is drawn.
  sheet.style.margin = `${(h * scale - h) / 2}px ${(w * scale - w) / 2}px`;
  $("#zoom-level").textContent = state.zoom ? `${Math.round(scale * 100)}%` : "Fit";
}

function nudgeZoom(direction) {
  const [w, h] = sheetSize();
  const canvas = $("#canvas");
  const fit = Math.min((canvas.clientWidth - 52) / w, (canvas.clientHeight - 52) / h);
  const current = state.zoom || fit;
  const next = Math.min(2, Math.max(0.25, current + direction * 0.15));
  state.zoom = Math.abs(next - fit) < 0.02 ? null : next;
  applyZoom();
}

/* --- actions -------------------------------------------------------------- */

async function build(button) {
  const label = button.querySelector(".btn-label");
  const original = label.textContent;
  button.dataset.busy = "1";
  button.disabled = true;
  label.textContent = "Building…";
  try {
    const data = await api("/api/build", { ...state });
    toast(`Built ${data.pages} pages · ${data.megabytes} MB`, "ok", data.pdf);
  } catch (error) {
    toast(error.message, "error");
  } finally {
    delete button.dataset.busy;
    button.disabled = false;
    label.textContent = original;
  }
}

async function saveConfig() {
  try {
    const data = await api("/api/save", { ...state, path: "family.yaml" });
    toast("Saved", "ok", data.saved);
  } catch (error) {
    toast(error.message, "error");
  }
}

/* --- wiring --------------------------------------------------------------- */

function bind() {
  $("#year").addEventListener("change", (e) => {
    const value = parseInt(e.target.value, 10);
    if (Number.isFinite(value) && value >= 1900 && value <= 2999) { state.year = value; refresh(); }
    else { e.target.value = state.year; toast("Year must be between 1900 and 2999", "error"); }
  });
  $("#family").addEventListener("input", (e) => { state.family_name = e.target.value; });
  $("#family").addEventListener("change", refresh);
  $("#size").addEventListener("change", (e) => {
    state.page_size = e.target.value; syncPreviewChoices(); applyZoom(); refresh();
  });
  $("#week").addEventListener("change", (e) => { state.week_starts = e.target.value; refresh(); });
  $("#dated").addEventListener("change", (e) => { state.dated_months = e.target.checked; refresh(); });

  $("#add-member").addEventListener("click", () => {
    if (state.members.length >= 10) return toast("Ten rows is the practical maximum", "error");
    state.members.push(""); renderMembers(); refresh();
  });
  $("#reset-pages").addEventListener("click", () => {
    state.pages = [...meta.defaultPages]; syncPreviewChoices(); renderPages(); refresh();
  });

  $("#preview-page").addEventListener("change", (e) => {
    state.preview = e.target.value; markCurrentPage(); refresh();
  });
  $("#zoom-in").addEventListener("click", () => nudgeZoom(1));
  $("#zoom-out").addEventListener("click", () => nudgeZoom(-1));
  $("#build").addEventListener("click", (e) => build(e.currentTarget));
  $("#save").addEventListener("click", saveConfig);

  window.addEventListener("resize", () => { if (!state.zoom) applyZoom(); });
  new ResizeObserver(() => { if (!state.zoom) applyZoom(); }).observe($("#canvas"));
  window.addEventListener("keydown", (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "b") { e.preventDefault(); build($("#build")); }
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "s") { e.preventDefault(); saveConfig(); }
  });
}

async function start() {
  try {
    meta = await api("/api/state");
  } catch (error) {
    toast(`Could not reach the planner: ${error.message}`, "error");
    return;
  }
  Object.assign(state, meta.config);
  $("#year").value = state.year;
  $("#family").value = state.family_name;
  $("#size").value = state.page_size;
  $("#week").value = state.week_starts;
  $("#dated").checked = state.dated_months;

  renderThemes(); renderTypefaces(); renderMembers();
  syncPreviewChoices(); renderPages();
  bind(); applyZoom(); loadPreview();
}

start();
