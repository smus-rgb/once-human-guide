/* Related entities from /links — pack stays read-only. Hooks openEntity. */
(function () {
  const ctx = document.getElementById("ctx");
  if (!ctx || !window.fetch) return;

  function chip(link) {
    const table = link.dst_table || link.src_table || "";
    const id = link.dst_id || link.src_id || "";
    const name = link.name || (table + "/" + id);
    return '<button class="chip" type="button" data-go-table="' + table + '" data-go-id="' + id + '">' +
      (link.relation || "link") + " · " + name + "</button>";
  }

  async function show(table, id) {
    if (!table || !id) return;
    try {
      const res = await fetch("/links/" + encodeURIComponent(table) + "/" + encodeURIComponent(id));
      if (!res.ok) return;
      const data = await res.json();
      const box = document.getElementById("ohg-links");
      const host = box || Object.assign(document.createElement("div"), { id: "ohg-links" });
      const links = data.links || [];
      host.innerHTML = "<h4 style='margin:12px 0 6px'>Vazby (" + links.length + ")</h4>" +
        (links.slice(0, 12).map(chip).join(" ") || "<span class='muted'>žádné odvozené vazby</span>");
      const body = ctx.querySelector(".body") || ctx;
      if (!box) body.appendChild(host);
    } catch (e) { /* offline pack */ }
  }

  document.addEventListener("click", function (ev) {
    const go = ev.target.closest("[data-go-table][data-go-id]");
    if (go && window.openEntity) {
      window.openEntity({ id: go.dataset.goId, _cat: go.dataset.goTable, name: go.textContent });
      return;
    }
    const item = ev.target.closest("[data-table][data-id]");
    if (item) show(item.dataset.table, item.dataset.id);
  });

  const orig = window.openEntity;
  if (typeof orig === "function") {
    window.openEntity = function (entity) {
      const result = orig.apply(this, arguments);
      const table = entity && (entity._cat || entity.table || entity.type);
      if (entity && entity.id && table) show(table, entity.id);
      return result;
    };
  }
})();
