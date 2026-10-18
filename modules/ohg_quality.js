/* Data quality panel — reads /audit, never writes the pack. */
(function () {
  if (!window.fetch) return;
  function card(summary, sample) {
    const rows = (summary || []).map(function (r) {
      return "<div class='chip'>" + r.severity + " · " + r.code + " · " + r.n + "</div>";
    }).join(" ") || "<span class='muted'>žádné nálezy</span>";
    const list = (sample || []).slice(0, 8).map(function (s) {
      return "<div class='muted'>" + (s.table_name || "") + "/" + (s.entity_id || "—") + " — " + (s.detail || s.code) + "</div>";
    }).join("");
    return "<div class='card' id='ohg-audit'><div class='kicker'>Databáze</div><b>Audit kvality</b><p class='muted'>Odvozeno při buildu SQLite. Pack se nemění.</p><div>" + rows + "</div>" + list + "</div>";
  }
  async function mount() {
    const view = document.getElementById("view");
    if (!view || document.getElementById("ohg-audit")) return;
    const route = (location.hash || "#/home").replace("#/", "").split("/")[0];
    if (route !== "home" && route !== "db" && route !== "settings") return;
    try {
      const res = await fetch("/audit");
      if (!res.ok) return;
      const data = await res.json();
      view.insertAdjacentHTML("beforeend", card(data.summary, data.sample));
    } catch (e) { /* offline */ }
  }
  window.addEventListener("hashchange", function () { setTimeout(mount, 40); });
  setTimeout(mount, 80);
})();
