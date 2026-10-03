/* System chip: API health and user favorites. Pack stays read-only. */
(function () {
  const badge = document.getElementById("syncBadge");
  async function ping() {
    if (!badge || !window.fetch) return;
    try {
      const res = await fetch("/health");
      if (!res.ok) throw new Error("health");
      const data = await res.json();
      badge.textContent = data.ok ? "DB " + (data.api_version || "ok") : "NO DB";
      badge.classList.toggle("on", !!data.ok);
    } catch (e) {
      badge.textContent = "OFFLINE";
    }
  }
  async function star(table, id, btn) {
    try {
      const res = await fetch("/user/favorites", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({table: table, id: id})
      });
      if (!res.ok) return;
      btn.textContent = "★ uloženo";
    } catch (e) { /* offline */ }
  }
  document.addEventListener("click", function (ev) {
    const item = ev.target.closest("[data-table][data-id]");
    if (!item || ev.target.closest(".ohg-star")) return;
    const ctx = document.querySelector("#ctx .body");
    if (!ctx || document.getElementById("ohg-star")) return;
    const btn = document.createElement("button");
    btn.className = "btn ghost ohg-star";
    btn.id = "ohg-star";
    btn.textContent = "☆ Oblíbené";
    btn.style.marginTop = "10px";
    btn.addEventListener("click", function () {
      star(item.dataset.table, item.dataset.id, btn);
    });
    ctx.appendChild(btn);
  });
  ping();
})();
