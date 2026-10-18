/* Self-heal — silent background pack upgrade + automatic repair of runtime errors.
   Nothing here talks to the user: every repair is applied immediately and recorded
   in localStorage 'ohg_repairs' (last 20) and in window.OHG_selfheal for inspection. */
(function () {
  if (!window.fetch || !window.OHG_DATA) return;
  const state = { repairs: [], pack: { checked: false, from: null, target: null, applied: false } };
  window.OHG_selfheal = state;

  function log(kind, detail) {
    const entry = { at: new Date().toISOString(), kind: kind, detail: String(detail || "").slice(0, 180) };
    state.repairs.push(entry);
    try {
      const ring = JSON.parse(localStorage.getItem("ohg_repairs") || "[]");
      ring.push(entry);
      localStorage.setItem("ohg_repairs", JSON.stringify(ring.slice(-20)));
    } catch (e) { /* no storage — the in-memory log still holds it */ }
  }
  /* sessionStorage keeps a repair from repeating within one session (no loops). */
  function once(key) {
    try {
      if (sessionStorage.getItem(key)) return false;
      sessionStorage.setItem(key, "1");
      return true;
    } catch (e) { return true; }
  }
  function shellReady() { return typeof render === "function" && typeof DATA !== "undefined"; }
  function packVersion() { return (typeof META !== "undefined" && (META.data_version || META.version)) || ""; }
  function workspaceEmpty() {
    const ws = document.getElementById("ws");
    return !ws || !ws.innerHTML.trim();
  }
  function safeRender() {
    try { render(); return true; } catch (e) {
      try { /* a broken view must not leave the app blank */
        if (location.hash && location.hash !== "#home") history.replaceState(null, "", "#home");
        render();
        log("redraw-home", e && e.message);
        return true;
      } catch (e2) { return false; }
    }
  }

  /* ── 1. Repair strategies — the first one that applies is applied at once ── */
  let errorHits = 0;
  const strategies = [
    { id: "redraw", applies: function () { return shellReady() && document.readyState !== "loading"; },
      fix: function () { safeRender(); } },
    { id: "reload", applies: function () { return workspaceEmpty() && once("ohg_heal_reload"); },
      fix: function () { location.reload(); } }
  ];
  function repair(reason, err) {
    errorHits++;
    const hit = strategies.filter(function (s) { return s.applies(); })[0];
    log("repair:" + (hit ? hit.id : "none"), reason + " — " + ((err && (err.message || err.status)) || ""));
    if (hit) hit.fix();
  }

  /* Retry a failed GET once — transient API/network failures heal themselves. */
  const nativeFetch = window.fetch;
  function retry(url, init, first) {
    const next = url + (url.indexOf("?") < 0 ? "?" : "&") + "retry=1";
    return new Promise(function (r) { setTimeout(r, 400); }).then(function () {
      return nativeFetch.call(window, next, init);
    }).then(function (res) {
      log("retry-ok", url + " -> " + res.status);
      return res;
    }, function (err) {
      log("retry-failed", url);
      if (first) return first;   /* hand the original response back */
      throw err;
    });
  }
  window.fetch = function (input, init) {
    const url = typeof input === "string" ? input : (input && input.url) || "";
    const method = ((init && init.method) || (input && input.method) || "GET").toUpperCase();
    const pending = nativeFetch.apply(this, arguments);
    if (method !== "GET" || url === "" || /[?&]retry=1/.test(url)) return pending;
    return pending.then(function (res) {
      return res.status >= 500 ? retry(url, init, res) : res;
    }, function () {
      return retry(url, init, null);   /* network level failure */
    });
  };

  /* ── 2. Automatic upgrade of the data pack (same origin, silent) ────────── */
  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      const s = document.createElement("script");
      s.src = src;
      s.onload = function () { s.remove(); resolve(true); };
      s.onerror = function () { s.remove(); reject(new Error("load failed: " + src)); };
      document.head.appendChild(s);
    });
  }
  /* A pending pack proposal is moot once the pack it describes is applied. */
  function dropStaleProposal(target) {
    if (typeof user === "undefined" || !Array.isArray(user.queue)) return;
    const kept = user.queue.filter(function (q) {
      return !(q.type === "pack-diff" && q.status === "pending" && q.id === "pack-" + target);
    });
    if (kept.length !== user.queue.length) {
      user.queue = kept;
      if (typeof saveUser === "function") saveUser();
    }
  }
  /* An upgrade is applied only when the new pack passes these checks, and the
     pack in use is snapshotted first, so a bad upgrade can be undone. */
  const SNAPSHOT_KEY = "ohg_pack_prev";
  function keepSnapshot(data, meta) {
    try {
      localStorage.setItem(SNAPSHOT_KEY, JSON.stringify({
        at: new Date().toISOString(), meta: meta || null, data: data || null
      }));
    } catch (e) { /* no room for the snapshot — the checks below still guard the upgrade */ }
  }
  function packProblem(pack, meta) {
    const tables = Object.keys(pack || {}).filter(function (k) { return Array.isArray(pack[k]); });
    if (!tables.length) return "pack nemá žádné tabulky";
    const records = tables.reduce(function (n, k) { return n + pack[k].length; }, 0);
    if (records < 50) return "pack obsahuje jen " + records + " záznamů";
    const declared = meta && meta.entities != null ? Number(meta.entities) : null;
    if (declared != null && Math.abs(declared - records) > Math.max(5, declared * 0.05)) {
      return "manifest uvádí " + declared + " záznamů, pack má " + records;
    }
    if (!String((meta && meta.version) || "").trim()) return "pack bez verze";
    return "";
  }
  function rollbackPack() {
    let snap = null;
    try { snap = JSON.parse(localStorage.getItem(SNAPSHOT_KEY) || "null"); } catch (e) { snap = null; }
    if (!snap || !snap.data) return false;
    window.OHG_DATA = snap.data;
    if (snap.meta) window.OHG_META = snap.meta;
    DATA = window.OHG_DATA;
    if (window.OHG_META) META = window.OHG_META;
    state.pack.rolledBackTo = packVersion();
    safeRender();
    log("pack-rollback", "návrat na " + packVersion());
    return true;
  }
  state.rollbackPack = rollbackPack;

  async function upgradePack() {
    try {
      const res = await window.fetch("version.json", { cache: "no-store" });
      if (!res.ok) return;
      const meta = await res.json();
      state.pack.checked = true;
      state.pack.from = packVersion();
      state.pack.target = meta.data_version || null;
      const target = state.pack.target;
      if (!target || target === state.pack.from || !once("ohg_pack_" + target)) return;
      await loadScript("ohg_data.js?v=" + encodeURIComponent(target));
      if (!window.OHG_DATA || !shellReady()) return;
      const problem = packProblem(window.OHG_DATA, window.OHG_META);
      if (problem) {
        log("pack-rejected", problem);
        rollbackPack();
        return;
      }
      keepSnapshot(DATA, typeof META === "undefined" ? null : META);
      DATA = window.OHG_DATA;
      if (window.OHG_META) META = window.OHG_META;
      state.pack.applied = packVersion() !== state.pack.from;
      if (state.pack.applied) {
        dropStaleProposal(target);
        safeRender();
        log("pack-upgrade", state.pack.from + " -> " + packVersion());
      } else {
        log("pack-check", "pack on the server still reports " + packVersion());
      }
    } catch (e) { /* offline — the loaded pack stays in use */ }
  }

  /* ── 3. Error sources worth healing ────────────────────────────────────── */
  window.addEventListener("error", function (ev) {
    if (ev.target && ev.target.tagName === "SCRIPT") { /* a module failed to load: fetch it again */
      const src = ev.target.getAttribute("src");
      if (!src || /[?&]heal=1/.test(src) || !once("ohg_heal_" + src)) return;
      loadScript(src + (src.indexOf("?") < 0 ? "?" : "&") + "heal=1").then(function () {
        log("module-reload", src);
        if (shellReady()) safeRender();
      }).catch(function () { /* the module is gone — the rest of the shell still runs */ });
      return;
    }
    repair("error", ev.error || ev.message || "unknown");
  });
  window.addEventListener("unhandledrejection", function (ev) { repair("rejection", ev.reason); });

  /* A corrupt local user layer crashes the shell before this script runs — reset it. */
  try { JSON.parse(localStorage.getItem("ohg_user") || "{}"); }
  catch (e) {
    localStorage.removeItem("ohg_user");
    log("reset-user-layer", "corrupt ohg_user JSON");
    if (once("ohg_heal_user")) location.reload();
  }

  upgradePack();
  setInterval(upgradePack, 600000);
})();
