/* Family Success Planner - preview UI.
   State lives in one object; every change re-renders the affected controls and
   asks the server for a fresh preview of the current page. */

const $ = (sel) => document.querySelector(sel);
const el = (tag, cls) => { const n = document.createElement(tag); if (cls) n.className = cls; return n; };

const MEMBER_DOTS = ["#5F7A62", "#C4A09A", "#C9956A", "#8AA084", "#A0909C", "#7A8B88"];

const state = {
  year: 2027, family_name: "", week_starts: "sunday", dated_months: true,
  cover_year: "auto", cover_text: "",
  page_size: "letter", members: [], pages: [], theme: "linen", fonts: "elegant",
  design: "original", type_size: { title: 30, cover: 66, body: 9, script: 13 },
  palette: {}, preview: null, zoom: null,
};
let meta = { themes: [], typefaces: [], designs: [], typeSizeRange: {}, catalogue: [], months: [], defaultPages: [], pageSizes: [], paletteRoles: [], themePalettes: {} };
let previewSeq = 0;

/* --- helpers -------------------------------------------------------------- */

function toast(message, kind = "", extra = "") {
  const node = $("#toast");
  node.textContent = "";
  const text = el("span");
  text.textContent = message;
  node.append(text);
  if (extra && extra.action && extra.path) {
    const btn = el("button");
    btn.type = "button";
    btn.textContent = extra.action;
    btn.addEventListener("click", () => openBuilt(extra.path));
    node.append(btn);
  } else if (typeof extra === "string" && extra) {
    const c = el("code");
    c.textContent = extra;
    node.append(c);
  }
  node.dataset.kind = kind;
  node.dataset.show = "1";
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => { node.dataset.show = "0"; }, kind === "error" ? 7000 : 8000);
}

function friendlyError(error, recovery) {
  const raw = String(error && error.message ? error.message : error || "");
  if (!raw || /^[A-Za-z]+Error:/.test(raw) || /malformed response/i.test(raw) || /failed to fetch/i.test(raw)) {
    return recovery;
  }
  return raw;
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
    input.addEventListener("change", () => {
      state.theme = theme.name;
      state.palette = {};
      renderThemes();
      renderPalette();
      refresh();
    });
    const name = el("span", "swatch-name");
    name.textContent = theme.name;
    label.append(input, chips, name);
    host.append(label);
  }
}

function hexForPicker(value) {
  const text = String(value || "").trim();
  const raw = text.startsWith("#") ? text.slice(1) : text;
  if (/^[0-9A-Fa-f]{3}$/.test(raw)) {
    return `#${raw[0]}${raw[0]}${raw[1]}${raw[1]}${raw[2]}${raw[2]}`.toLowerCase();
  }
  if (/^[0-9A-Fa-f]{6}$/.test(raw)) return `#${raw}`.toLowerCase();
  return "";
}

function themeColors(name) {
  const palettes = meta.themePalettes || {};
  return palettes[name] || palettes[meta.themes?.[0]?.name] || {};
}

function currentPalette() {
  return { ...themeColors(state.theme), ...(state.palette || {}) };
}

function hasPaletteOverrides() {
  return Object.keys(state.palette || {}).length > 0;
}

function setPaletteToken(key, hex) {
  const next = hexForPicker(hex);
  if (!next) return false;
  const base = (themeColors(state.theme)[key] || "").toUpperCase();
  const palette = { ...(state.palette || {}) };
  if (next.toUpperCase() === base) delete palette[key];
  else palette[key] = next.toUpperCase();
  state.palette = palette;
  return next;
}

function renderPalette() {
  const host = $("#palette");
  if (!host) return;
  host.textContent = "";
  const resolved = currentPalette();
  const base = themeColors(state.theme);
  for (const role of meta.paletteRoles || []) {
    const value = hexForPicker(resolved[role.id] || "#000000") || "#000000";
    const replaced = (value.toUpperCase() !== (base[role.id] || "").toUpperCase());

    const row = el("div", "palette-row");
    row.dataset.replaced = replaced ? "1" : "0";

    const name = el("span", "palette-name");
    name.textContent = role.label;

    const picker = el("input");
    Object.assign(picker, { type: "color", value });
    picker.setAttribute("aria-label", `${role.label} colour`);
    picker.addEventListener("input", () => {
      const applied = setPaletteToken(role.id, picker.value);
      if (applied) hex.value = applied.toUpperCase();
      row.dataset.replaced = (state.palette || {})[role.id] ? "1" : "0";
      undo.hidden = !(state.palette || {})[role.id];
      syncPaletteReset();
      refresh();
    });

    const hex = el("input");
    Object.assign(hex, { type: "text", value: value.toUpperCase(), spellcheck: false });
    hex.setAttribute("aria-label", `${role.label} hex colour`);
    hex.maxLength = 7;
    hex.addEventListener("change", () => {
      const applied = setPaletteToken(role.id, hex.value);
      if (!applied) {
        hex.value = (currentPalette()[role.id] || value).toUpperCase();
        toast("Use a hex colour like #3E5344.", "error");
        return;
      }
      picker.value = applied;
      hex.value = applied.toUpperCase();
      row.dataset.replaced = (state.palette || {})[role.id] ? "1" : "0";
      undo.hidden = !(state.palette || {})[role.id];
      syncPaletteReset();
      refresh();
    });

    const undo = el("button", "palette-undo");
    undo.type = "button";
    undo.textContent = "Reset";
    undo.hidden = !replaced;
    undo.setAttribute("aria-label", `Reset ${role.label} to the theme colour`);
    undo.addEventListener("click", () => {
      const restored = hexForPicker(base[role.id]) || value;
      setPaletteToken(role.id, restored);
      picker.value = restored;
      hex.value = restored.toUpperCase();
      row.dataset.replaced = "0";
      undo.hidden = true;
      syncPaletteReset();
      refresh();
    });

    row.append(name, picker, hex, undo);
    host.append(row);
  }
  syncPaletteReset();
}

function syncPaletteReset() {
  const btn = $("#reset-palette");
  if (btn) btn.hidden = !hasPaletteOverrides();
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

const SIZE_ROLES = [
  ["title", "Titles"],
  ["cover", "Cover"],
  ["body", "Body"],
  ["script", "Script"],
];

function clampSize(key, value) {
  const range = meta.typeSizeRange[key] || { min: 6, max: 96 };
  if (!Number.isFinite(value)) return state.type_size[key];
  return Math.min(range.max, Math.max(range.min, Math.round(value * 10) / 10));
}

function renderSizes() {
  const host = $("#sizes");
  host.textContent = "";
  for (const [key, label] of SIZE_ROLES) {
    const range = meta.typeSizeRange[key] || { min: 6, max: 96, value: state.type_size[key] };
    const row = el("div", "size-row");
    const name = el("span");
    name.textContent = label;
    const slider = el("input");
    Object.assign(slider, {
      type: "range", min: range.min, max: range.max, step: "0.5",
      value: state.type_size[key],
    });
    slider.setAttribute("aria-label", `${label} size`);
    const num = el("input");
    Object.assign(num, {
      type: "number", min: range.min, max: range.max, step: "0.5",
      value: state.type_size[key],
    });
    num.setAttribute("aria-label", `${label} size in points`);
    const apply = (raw) => {
      const next = clampSize(key, parseFloat(raw));
      state.type_size[key] = next;
      slider.value = next;
      num.value = next;
      refresh();
    };
    slider.addEventListener("input", () => apply(slider.value));
    num.addEventListener("change", () => apply(num.value));
    row.append(name, slider, num);
    host.append(row);
  }
}

function renderDesigns() {
  const host = $("#designs");
  host.textContent = "";
  for (const look of meta.designs) {
    const card = el("label", "design-card");
    card.dataset.on = state.design === look.id ? "1" : "0";
    const input = el("input");
    Object.assign(input, { type: "radio", name: "design", value: look.id,
                           checked: state.design === look.id });
    input.addEventListener("change", () => { state.design = look.id; renderDesigns(); refresh(); });
    const name = el("strong");
    name.textContent = look.label;
    const note = el("em");
    note.textContent = look.note;
    card.append(input, name, note);
    host.append(card);
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
    Object.assign(input, { type: "text", value, placeholder: "Maya" });
    input.setAttribute("aria-label", `Name ${index + 1}`);
    input.addEventListener("input", () => { state.members[index] = input.value; });
    input.addEventListener("change", refresh);
    const remove = el("button");
    remove.type = "button";
    remove.textContent = "×";
    remove.setAttribute("aria-label", `Remove name ${index + 1}`);
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
  const size = (meta.pageSizes || []).find((s) => s.id === state.page_size);
  const label = size ? size.label : "8.5 × 11 in";
  $("#brand-sub").textContent = `${pages.length} page${pages.length === 1 ? "" : "s"} · ${label}`;
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
    if (seq === previewSeq) {
      toast(friendlyError(error, "Could not update the preview. Keep the planner window open and try again."), "error");
    }
  } finally {
    if (seq === previewSeq) $("#spinner").hidden = true;
  }
}

/* Page size in CSS pixels at 96dpi, so the sheet matches the paper choice. */
function sheetSize() {
  const size = (meta.pageSizes || []).find((s) => s.id === state.page_size);
  const widthIn = size ? size.width : 8.5;
  const heightIn = size ? size.height : 11;
  return [Math.round(widthIn * 96), Math.round(heightIn * 96)];
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
  $("#zoom-level").textContent = state.zoom ? `${Math.round(scale * 100)}%` : "Fit page";
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
  label.textContent = "Making PDF…";
  try {
    const data = await api("/api/build", { ...state });
    toast("Your PDF is ready to print.", "ok", { action: "Open PDF", path: data.pdf });
  } catch (error) {
    toast(friendlyError(error, "Could not make the PDF. Keep the planner window open and try again."), "error");
  } finally {
    delete button.dataset.busy;
    button.disabled = false;
    label.textContent = original;
  }
}

async function downloadPlan() {
  try {
    const data = await api("/api/export", { ...state });
    const blob = new Blob([data.markdown], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = data.filename || "family-planner.md";
    document.body.append(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    toast("Downloaded your plan. Keep that file for next year, or send it to a friend.", "ok");
  } catch (error) {
    toast(friendlyError(error, "Could not download the plan. Keep the planner window open and try again."), "error");
  }
}

async function importPlanFile(file) {
  try {
    const text = await file.text();
    const data = await api("/api/import", { text });
    Object.assign(state, data.config);
    if (!(meta.pageSizes || []).some((s) => s.id === state.page_size)) state.page_size = "letter";
    state.type_size = { title: 30, cover: 66, body: 9, script: 13, ...(state.type_size || {}) };
    state.palette = data.config.palette || {};
    paintForm();
    refresh();
    toast("Loaded that plan. Change the year or the name, then make a PDF.", "ok");
  } catch (error) {
    toast(friendlyError(error, "Could not open that file. Use a plan you downloaded, or a family.yaml."), "error");
  }
}

async function openBuilt(path) {
  try {
    await api("/api/open", { path });
  } catch (error) {
    toast(friendlyError(error, "Could not open the PDF. Make a PDF again, then open it from here."), "error");
  }
}

function paintForm() {
  $("#year").value = state.year;
  $("#cover-text").value = state.cover_text || "";
  $("#family").value = state.family_name;
  $("#size").value = state.page_size;
  $("#week").value = state.week_starts;
  $("#dated").checked = state.dated_months;
  if (!state.cover_year) state.cover_year = "auto";
  syncCoverYearRow();
  renderThemes(); renderPalette(); renderTypefaces(); renderSizes(); renderDesigns(); renderMembers();
  syncPreviewChoices(); renderPages();
}

function newBook() {
  state.family_name = "";
  state.cover_text = "";
  state.members = ["", ""];
  state.pages = [...meta.defaultPages];
  state.theme = "linen";
  state.palette = {};
  state.fonts = "elegant";
  state.design = "original";
  state.dated_months = true;
  state.cover_year = "auto";
  state.week_starts = "sunday";
  state.page_size = "letter";
  state.type_size = { title: 30, cover: 66, body: 9, script: 13 };
  state.preview = "cover";
  paintForm();
  refresh();
  toast("Cleared this screen. Download a plan if you want to keep these choices.");
}

/* --- wiring --------------------------------------------------------------- */

function syncCoverYearRow() {
  const row = $("#cover-year-row");
  row.hidden = state.dated_months;
  const select = $("#cover-year");
  const mode = state.cover_year;
  select.value = (mode === "omit" || mode === "print" || mode === "blank") ? mode : "blank";
}

function bind() {
  $("#year").addEventListener("change", (e) => {
    const value = parseInt(e.target.value, 10);
    if (Number.isFinite(value) && value >= 1900 && value <= 2999) { state.year = value; refresh(); }
    else { e.target.value = state.year; toast("Enter a year between 1900 and 2999.", "error"); }
  });
  $("#cover-text").addEventListener("input", (e) => {
    state.cover_text = e.target.value;
    refresh();
  });
  $("#family").addEventListener("input", (e) => { state.family_name = e.target.value; });
  $("#family").addEventListener("change", refresh);
  $("#size").addEventListener("change", (e) => {
    state.page_size = e.target.value; syncPreviewChoices(); applyZoom(); refresh();
  });
  $("#week").addEventListener("change", (e) => { state.week_starts = e.target.value; refresh(); });
  $("#dated").addEventListener("change", (e) => {
    state.dated_months = e.target.checked;
    if (!state.dated_months && (state.cover_year === "auto" || !state.cover_year)) {
      state.cover_year = "blank";
    }
    syncCoverYearRow();
    refresh();
  });
  $("#cover-year").addEventListener("change", (e) => {
    state.cover_year = e.target.value;
    refresh();
  });

  $("#add-member").addEventListener("click", () => {
    if (state.members.length >= 10) return toast("You can list up to 10 people.", "error");
    state.members.push(""); renderMembers(); refresh();
  });
  $("#reset-pages").addEventListener("click", () => {
    state.pages = [...meta.defaultPages]; syncPreviewChoices(); renderPages(); refresh();
  });
  $("#reset-palette").addEventListener("click", () => {
    state.palette = {};
    renderPalette();
    refresh();
  });

  $("#preview-page").addEventListener("change", (e) => {
    state.preview = e.target.value; markCurrentPage(); refresh();
  });
  $("#zoom-in").addEventListener("click", () => nudgeZoom(1));
  $("#zoom-out").addEventListener("click", () => nudgeZoom(-1));
  $("#build").addEventListener("click", (e) => build(e.currentTarget));
  $("#download").addEventListener("click", downloadPlan);
  $("#open-plan").addEventListener("click", () => $("#plan-file").click());
  $("#plan-file").addEventListener("change", (e) => {
    const file = e.target.files && e.target.files[0];
    e.target.value = "";
    if (file) importPlanFile(file);
  });
  $("#fresh").addEventListener("click", newBook);

  window.addEventListener("resize", () => { if (!state.zoom) applyZoom(); });
  new ResizeObserver(() => { if (!state.zoom) applyZoom(); }).observe($("#canvas"));
  window.addEventListener("keydown", (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "b") { e.preventDefault(); build($("#build")); }
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "s") { e.preventDefault(); downloadPlan(); }
  });
}

async function start() {
  try {
    meta = await api("/api/state");
  } catch (error) {
    toast("Could not open the planner. Double-click start-planner and leave that window open.", "error");
    return;
  }
  Object.assign(state, meta.config);
  if (!state.design) state.design = "original";
  if (!(meta.pageSizes || []).some((s) => s.id === state.page_size)) state.page_size = "letter";
  state.type_size = { title: 30, cover: 66, body: 9, script: 13, ...(state.type_size || {}) };
  state.palette = state.palette || {};
  paintForm();
  bind(); applyZoom(); loadPreview();
}

start();
