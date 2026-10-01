# Once Human Guide — živý plán

Po dokončení fáze se **hotová fáze z tohoto souboru maže**.
Dokončeno 2026-09-30: **Fáze A — Stabilizace**.
Dokončeno 2026-10-01: **Fáze B — Kompletní archivy** (`OnceHumanGuide_v18.0.0_complete.zip`, legacy v `archive/legacy/`, GitHub release `v18.0.0`).
Dokončeno 2026-10-01: **Fáze C — Doladění systému** (tenký host v19 + `modules/*.js`, pack channel, mapa region/tiles, build export, API `/ui` + `/update/check`).

---

## 0. Principy (platí po celou dobu)

1. **Jedna pravda o datech** — pack (`ohg_data.js` / JSON / DB) je kanonický; UI jen čte.
2. **User layer odděleně** — favorites, inventory, builds, queue nikdy nemění pack.
3. **GitHub = jediný distribuční bod** — installer, updater, release zip, tags.
4. **Archiv = kompletní snapshot verze**, ne „nejnovější soubor někde v folderu“.
5. **Emergent Labs** — spolupráce výhradně přes GitHub (issues, PR, branches, CODEOWNERS).

---

## Fáze D — GitHub + Emergent Labs (průběžně)

- Issues, Projects board, PR-only merge, CODEOWNERS
- Labs: fork nebo `labs/*`; data jen PR; UI experimenty `labs/ui-*`
- PR checklist: offline HTML, count entit, CHANGELOG
- Sync v18 na `main` hotový (2026-10-01, `54835f4`). Lokálně hotovo: `.github/CODEOWNERS`, `.github/PULL_REQUEST_TEMPLATE.md`. Zbývá push na GitHub, Projects board, pozvat Labs.

---

## Fáze E — Provoz a data (měsíční rytmus)

1. Po herním patchi: JSON → regenerace packu → bump version → Agent queue
2. Měsíční archive freeze
3. Čtvrtletní review AdaptiveShell / SW
4. Staré shelly `v6…v17` jen v `archive/shells/` (kopie už jsou; root kopie zatím zůstávají)

---

## Další 3 kroky

1. Push v19 + modules + CODEOWNERS + PR template na `main` a tag `v19.0.0`
2. GitHub Projects board (backlog D/E)
3. Pozvat Emergent Labs jako collaborator (fork / `labs/*`, ne přímý push)
