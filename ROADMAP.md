# Once Human Guide — živý plán

Po dokončení fáze se **hotová fáze z tohoto souboru maže**.
Dokončeno 2026-09-30: **Fáze A — Stabilizace**.
Dokončeno 2026-10-01: **Fáze B — Kompletní archivy** (`OnceHumanGuide_v18.0.0_complete.zip`, legacy v `archive/legacy/`, GitHub release `v18.0.0`).
Dokončeno 2026-10-01: **Fáze C.1 — data/API integrity** (souřadnice, effect, FTS, `/integrity`, static shell).
Dokončeno 2026-10-01: **Fáze C — Doladění systému** (tenký host v19 + `modules/*.js`, pack channel, mapa region/tiles, build export, API `/ui` + `/update/check`). GitHub `main` `e103185`.

---

## 0. Principy (platí po celou dobu)

1. **Jedna pravda o datech** — pack (`ohg_data.js` / JSON / DB) je kanonický; UI jen čte.
2. **User layer odděleně** — favorites, inventory, builds, queue nikdy nemění pack.
3. **GitHub = jediný distribuční bod** — installer, updater, release zip, tags.
4. **Archiv = kompletní snapshot verze**, ne „nejnovější soubor někde v folderu“.
5. **Emergent Labs** — spolupráce výhradně přes GitHub (issues, PR, branches, CODEOWNERS).

---

## Fáze D — GitHub + Emergent Labs (průběžně, neuzavřeno)

Hotovo 2026-10-01:
- `main` má v19 + `modules/` + `.github/CODEOWNERS` + `PULL_REQUEST_TEMPLATE.md` (`e103185`)
- `docs/COLLAB.md`, issue templates (`bug`, `data`, `labs`)
- Issues jako náhrada Projects boardu (GitHub Projects API není v konektoru)

Zbývá (blokuje uzavření fáze):
- GitHub login Emergent Labs — bez něj nejde collaborator ani CODEOWNERS řádek
- Projects board v UI (ručně, nebo až bude API)
- Tag `v19.0.0` — create-release nástroj v konektoru není; release se zakládá v UI z `main`

---

## Fáze E — Provoz a data (měsíční rytmus)

1. Po herním patchi: JSON → regenerace packu → bump version → Agent queue
2. Měsíční archive freeze
3. Čtvrtletní review AdaptiveShell / SW
4. Staré shelly `v6…v17` jen v `archive/shells/` (kopie už jsou; root kopie zatím zůstávají)

---

## Další 3 kroky

1. Dodat GitHub login Emergent Labs a přidat collaborator (fork / `labs/*`, ne přímý push)
2. V GitHub UI založit Projects board a release `v19.0.0` z `main`
3. První Labs PR proti checklistu v `docs/COLLAB.md`
