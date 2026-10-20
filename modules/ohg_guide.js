/* Průvodce hráčem — obsah z /guide (Google Drive) nebo z guide.json (SW cache).
   Vyhledávací pole filtruje cesty i kroky podle názvu, cíle a klíčových slov.
   Pack zůstává jen ke čtení, postup hráče jde do user layer. */
(function () {
  const navPlay = (typeof NAV !== "undefined" ? NAV : []).find(function (g) { return g.g === "Play"; });
  if (navPlay && !navPlay.items.some(function (i) { return i.id === "guide"; })) {
    navPlay.items.unshift({ id: "guide", label: "Guide", ic: "📖" });
  }
  if (typeof PHONE_MORE !== "undefined" && PHONE_MORE.indexOf("guide") < 0) PHONE_MORE.push("guide");
  // Runtime už menu jednou postavil — bez překreslení by položka chyběla do prvního kliknutí.
  if (typeof renderNav === "function") renderNav();

  let GUIDE = null, source = "local", q = "", pendingStep = null, started = false;
  const open = {};

  function norm(s) { return String(s == null ? "" : s).toLowerCase(); }
  function kw(o) { return (o.keywords || []).concat(o.tags || []).join(" "); }
  function esc(s) { return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;"); }
  function steps() {
    const out = [];
    ((GUIDE && GUIDE.paths) || []).forEach(function (p) {
      (p.steps || []).forEach(function (s) {
        out.push(Object.assign({}, s, { _path: p.id, _pathTitle: p.title }));
      });
    });
    return out;
  }
  function hit(o, query) {
    return norm([o.title, o.name, o.goal, o.why, o.summary, kw(o)].join(" ")).indexOf(query) >= 0;
  }
  function done(id) { return !!(user.guideProgress && user.guideProgress[id]); }

  async function load() {
    if (GUIDE || started) return;
    started = true;
    try {
      const res = await fetch("guide", { cache: "no-store" });
      if (res.ok) {
        const doc = await res.json();
        if (doc && doc.paths) {
          GUIDE = doc;
          source = (doc.meta && doc.meta.source) || "local";
          return;
        }
      }
    } catch (e) { /* offline → statický soubor */ }
    try {
      const local = await fetch("guide.json", { cache: "no-store" });
      if (local.ok) { GUIDE = await local.json(); source = "local"; }
    } catch (e) { /* bez guide.json zůstane prázdno */ }
  }

  function stepRow(s) {
    return '<button class="item" onclick="ohgGuideOpen(\'' + s.id + '\')">' +
      '<div><b>' + esc(s.title) + '</b><div class="muted">' + esc(s._pathTitle) +
      (s.time_estimate ? " · " + esc(s.time_estimate) : "") + '</div></div>' +
      '<span class="chip">' + (done(s.id) ? "✓" : "→") + '</span></button>';
  }

  function results() {
    const query = norm(q).trim();
    if (!query || !GUIDE) return "";
    const stepHits = steps().filter(function (s) { return hit(s, query); });
    const faqHits = (GUIDE.faq || []).filter(function (f) { return hit({ title: f.q, goal: f.a, keywords: f.keywords }, query); });
    const termHits = (GUIDE.glossary || []).filter(function (g) { return hit({ title: g.term, goal: g.definition, keywords: g.keywords }, query); });
    const total = stepHits.length + faqHits.length + termHits.length;
    return '<div class="card" style="margin-bottom:10px"><div class="kicker">Výsledky</div><b>' +
      stepHits.length + ' kroků · ' + faqHits.length + ' FAQ · ' + termHits.length + ' pojmů</b>' +
      '<div class="muted" style="font-size:12px">Filtr prochází název, cíl, proč a klíčová slova.</div></div>' +
      (total ? '<div class="list">' +
        stepHits.map(stepRow).join("") +
        faqHits.map(function (f) { return '<div class="item"><div><b>' + esc(f.q) + '</b><div class="muted">' + esc(f.a) + '</div></div></div>'; }).join("") +
        termHits.map(function (g) { return '<div class="item"><div><b>' + esc(g.term) + '</b><div class="muted">' + esc(g.definition) + '</div></div></div>'; }).join("") +
        '</div>' : '<div class="card muted">Nic nenalezeno — zkus jiné klíčové slovo (např. deviation, silo, build).</div>');
  }

  function stepDetail(s) {
    const links = (s.links || []).map(function (l) {
      const rows = DATA[l.table] || [];
      const e = rows.find(function (x) { return String(x.id) === String(l.id); });
      if (!e) return '<span class="chip">' + esc(l.label || l.id) + '</span>';
      const payload = JSON.stringify(Object.assign({}, e, { _cat: l.table })).replace(/'/g, "&#39;");
      return '<button class="chip" style="cursor:pointer" onclick=\'openEntity(' + payload + ')\'>' + esc(l.label || e.name) + '</button>';
    }).join(" ");
    const list = function (arr, tag) {
      if (!arr || !arr.length) return "";
      return '<' + tag + ' style="margin:6px 0 0 18px;padding:0">' +
        arr.map(function (x) { return '<li style="margin:4px 0">' + esc(x) + '</li>'; }).join("") + '</' + tag + '>';
    };
    return '<div class="kicker">Guide · ' + esc(s._pathTitle || "") + '</div>' +
      '<h2 style="margin:4px 0 8px">' + esc(s.title) + '</h2>' +
      '<label class="row" style="margin-bottom:8px"><input type="checkbox" ' + (done(s.id) ? "checked" : "") +
      ' onchange="ohgGuideDone(\'' + s.id + '\',this.checked)"/> Splněno</label>' +
      (s.goal ? '<div style="margin:8px 0"><span class="muted">Cíl</span><div>' + esc(s.goal) + '</div></div>' : "") +
      (s.why ? '<div style="margin:8px 0"><span class="muted">Proč</span><div>' + esc(s.why) + '</div></div>' : "") +
      (s.actions && s.actions.length ? '<div style="margin:8px 0"><span class="muted">Postup</span>' + list(s.actions, "ol") + '</div>' : "") +
      (s.tips && s.tips.length ? '<div class="card" style="margin-top:8px"><div class="kicker">Tip</div>' + s.tips.map(function (t) { return "<div>" + esc(t) + "</div>"; }).join("") + '</div>' : "") +
      (links ? '<div style="margin-top:10px"><span class="muted">V databázi</span><div class="row" style="margin-top:6px">' + links + '</div></div>' : "") +
      (s.verified_at || (s.source_refs || []).length
        ? '<p class="muted" style="font-size:11px;margin-top:10px">Zdroj: ' + esc((s.source_refs || []).join(", ")) +
          (s.verified_at ? " · ověřeno " + esc(s.verified_at) : "") + '</p>' : "");
  }

  function view() {
    if (!GUIDE) {
      load().then(function () { if (route === "guide") render(); });
      return '<div class="kicker">Guide</div><h1>Průvodce hráčem</h1><p class="sub">Načítám obsah průvodce…</p>';
    }
    if (pendingStep) {
      const id = pendingStep;
      pendingStep = null;
      setTimeout(function () { ohgGuideOpen(id); }, 0);
    }
    const all = steps();
    const paths = GUIDE.paths || [];
    const doneAll = all.filter(function (s) { return done(s.id); }).length;
    const pathsHtml = paths.map(function (p) {
      const list = p.steps || [];
      const d = list.filter(function (s) { return done(s.id); }).length;
      const pct = list.length ? Math.round(d / list.length * 100) : 0;
      const isOpen = open[p.id] !== false;
      return '<div class="card" style="margin-bottom:10px">' +
        '<div class="row" style="justify-content:space-between;align-items:flex-start">' +
        '<div><div class="kicker">' + esc(p.phase || p.id) + '</div><b>' + esc(p.title) + '</b>' +
        '<div class="muted" style="font-size:12px">' + esc(p.summary || "") + '</div></div>' +
        '<button class="btn ghost" onclick="ohgGuideToggle(\'' + p.id + '\')">' + (isOpen ? "−" : "+") + '</button></div>' +
        (isOpen
          ? '<div class="progress" style="margin:8px 0"><i style="width:' + pct + '%"></i></div>' +
            '<div class="muted" style="font-size:12px">' + d + "/" + list.length + ' kroků</div>' +
            '<div class="list" style="margin-top:8px">' + list.map(function (s) { return stepRow(Object.assign({}, s, { _pathTitle: p.title })); }).join("") + '</div>'
          : "") +
        '</div>';
    }).join("");
    const faqHtml = (GUIDE.faq || []).map(function (f) {
      return '<details class="card" style="margin-bottom:8px"><summary style="cursor:pointer"><b>' + esc(f.q) + '</b></summary>' +
        '<p class="muted" style="margin:8px 0 0">' + esc(f.a) + '</p></details>';
    }).join("");
    const glosHtml = (GUIDE.glossary || []).map(function (g) {
      return '<div class="item"><div><b>' + esc(g.term) + '</b><div class="muted">' + esc(g.definition) + '</div></div></div>';
    }).join("");
    const searching = !!norm(q).trim();
    return '<div class="kicker">Guide · ' + esc(source) + '</div><h1>Průvodce hráčem</h1>' +
      '<p class="sub">' + paths.length + ' cest · ' + all.length + ' kroků · splněno ' + doneAll +
      ' · obsah: guide.json' + (source === "drive" ? " + Google Drive" : "") + '</p>' +
      '<div class="filters"><input id="ohg-guide-q" autocomplete="off" style="flex:1;min-width:200px" ' +
      'placeholder="Hledat v průvodci — název nebo klíčová slova…" value="' + esc(q) + '" oninput="ohgGuideQuery(this.value)"/></div>' +
      '<div id="ohg-guide-results">' + results() + '</div>' +
      '<div id="ohg-guide-paths"' + (searching ? ' style="display:none"' : "") + '>' + pathsHtml +
      '<div class="kicker" style="margin-top:14px">FAQ</div>' + faqHtml +
      '<div class="kicker" style="margin-top:14px">Slovníček</div><div class="list">' + glosHtml + '</div></div>';
  }

  window.ohgGuideQuery = function (value) {
    q = value;
    const box = document.getElementById("ohg-guide-results");
    const paths = document.getElementById("ohg-guide-paths");
    if (box) box.innerHTML = results();
    if (paths) paths.style.display = norm(q).trim() ? "none" : "";
  };
  window.ohgGuideToggle = function (id) {
    open[id] = open[id] === false;
    render();
  };
  window.ohgGuideDone = function (id, value) {
    if (!user.guideProgress) user.guideProgress = {};
    user.guideProgress[id] = !!value;
    saveUser();
    toast(value ? "Krok splněn" : "Krok vrácen");
    if (route === "guide" && device !== "phone") render();
  };
  window.ohgGuideOpen = function (id) {
    const s = steps().find(function (x) { return x.id === id; });
    if (!s) return;
    const html = stepDetail(s);
    if (device === "phone") {
      document.getElementById("ov").classList.add("on");
      const sheet = document.getElementById("sheet");
      sheet.className = "sheet on";
      sheet.innerHTML = html;
    } else {
      setCtx(html);
    }
  };

  const baseViewHome = window.viewHome;
  window.viewHome = function () { return route === "guide" ? view() : baseViewHome.apply(this, arguments); };

  const baseSearch = window.search;
  window.search = function (query) {
    const base = baseSearch.apply(this, arguments) || [];
    const query2 = norm(query).trim();
    if (!query2 || !GUIDE) return base;
    const hits = steps().filter(function (s) { return hit(s, query2); }).slice(0, 6).map(function (s) {
      return { id: s.id, name: s.title, desc: s.goal || "", keys: kw(s), _cat: "guide", _guide: true };
    });
    // Kroky průvodce jdou první: paleta i výsledky řežou seznam na 20 položek.
    return hits.concat(base);
  };

  const baseOpenEntity = window.openEntity;
  window.openEntity = function (e) {
    if (e && e._guide) { ohgGuideOpen(e.id); return; }
    return baseOpenEntity.apply(this, arguments);
  };

  const baseBootHash = window.bootHash;
  window.bootHash = function () {
    baseBootHash.apply(this, arguments);
    const parts = (location.hash || "").replace(/^#/, "").split("/");
    if (parts[0] === "guide") {
      route = "guide";
      if (parts[1]) pendingStep = decodeURIComponent(parts[1]);
    }
  };

  load();
})();
