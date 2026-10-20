# Once Human Guide — živý plán

Po dokončení fáze se **hotová fáze z tohoto souboru maže**.
Dokončeno 2026-09-30: **Fáze A — Stabilizace**.
Dokončeno 2026-10-01: **Fáze B — Kompletní archivy** (`OnceHumanGuide_v18.0.0_complete.zip`, legacy v `archive/legacy/`, GitHub release `v18.0.0`).
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

## Plán 2026-10-20 — profesionální in-app průvodce hráče

Priorita: **Android (Expo)**. Průvodce je datováno verzovaný obsah, který čtou všichni klienti (shell v19 i Expo) — jedna pravda, jeden `guide.json`.

---

## Fáze F — Expo klient: zdroj v repu (blokuje Android)

Dnes `expo-app/` obsahuje jen `app.json`, `package.json` a `README.md` — zdroj žije mimo GitHub, takže Android build nejde reprodukovat.

1. Přesunout zdroj Expo app do `expo-app/` (`app/` routes, `src/`, `package-lock.json`, `eas.json`).
2. `expo-app/README.md` — setup (`npm install`, `npx expo start`), API base URL, jak app pustit na telefonu přes Expo Go.
3. Klient čte pack z API (`/export`, `/version`) nebo z lokálního `pack.json` generovaného z JSON modulů — žádná druhá pravda o datech.
4. Hotovo, když: čistý klon repa → `npx expo start` → app zobrazí databázi z packu na telefonu.

---

## Fáze G — Obsah průvodce (data)

Nový modul `guide.json` zapojený do pack pipeline (`db_build.py` MODULES, `regen_pack.py`, `version.json.files`).

1. Cesty podle fáze hráče: **Nováček** (0–2 h), **Early** (první zbraň, deviation, silo), **Mid** (farm, recipes, territory), **Endgame** (boss, monolith, build), **PvP**.
2. Struktura kroku: `id`, `phase`, `title`, `goal`, `why`, `steps[]`, `links[]` (id entit z packu), `time_estimate`, `source_refs`, `verified_at`.
3. Onboarding (prvních 60 s), FAQ, slovníček pojmů a krátké kontextové tipy k entitám.
4. Hotovo, když: CI test ověří, že každý `links[].id` existuje v packu a že počet kroků odpovídá `version.json`.

---

## Fáze H — Android: obrazovky průvodce (priorita)

1. **Guide Home** — výběr cesty podle fáze hráče + „pokračuj, kde jsi skončil“.
2. **Detail kroku** — goal / why / steps, odkazy na entity (zbraň, deviation, lokace), tlačítko „splněno“.
3. **Checklist + progress** — stav kroku patří do user layer, nikdy do packu.
4. **Kontextová nápověda** — „?“ v detailu entity: co s tím dělat, kde to padá, s čím to kombinovat.
5. **Hledání v průvodci** — stejný index jako databáze, čeština bez diakritiky.
6. **Offline** — obsah průvodce v AsyncStorage/SQLite, synchronizace při připojení.
7. Hotovo, když: nový hráč projde onboarding → první krok → odškrtnutí i bez sítě.

---

## Fáze I — Parita v shellu v19 (testbed obsahu)

1. `modules/ohg_guide.js` jako modul v sekci **Play** (NAV v `ohg_runtime.js`).
2. Stejný `guide.json` i stejné chování jako v Androidu.
3. Slouží jako rychlá smyčka pro psaní obsahu a pro offline PWA.
4. Hotovo, když: `once_human_guide_v19.html` otevřený offline vykreslí průvodce z cache.

---

## Fáze J — Kvalita, měření a release do Play

1. Testy: obsah průvodce (odkazy na entity, počty), API smoke, průchod onboardingem.
2. **CI gate** — zrušit `pytest -q || true` v `.github/workflows/python-app.yml` a doplnit, co `version.json` už deklaruje, ale v repu chybí: `tests/` a `modules/ohg_selfheal.js` (chybějící soubor shodí instalaci service workeru).
3. Sjednotit verzování: `app_version` 5.5.0 vs 3.0.0 (`react-app`, `expo-app`), `records` 373 vs 372, cache `ohg-v19.2-307` vs `ohg-2026-10-09-v19.2-372`.
4. Přístupnost a čeština: touch target 44 px, kontrast, reduced motion, diakritika; u každého kroku zdroj a datum ověření.
5. Měření (opt-in): které kroky hráči dokončují a kde odpadají.
6. Release: EAS build → Play Console internal testing, data safety + privacy policy, store listing, tag podle semver.
7. Hotovo, když: build běží v internal testingu a `RELEASE_CHECKLIST.md` je rozšířený o Play.

---

## Další 3 kroky

1. Přesunout zdroj Expo app do `expo-app/` a rozjet `npx expo start` z čistého klonu
2. Založit `guide.json` s cestou Nováček (10 kroků) a protáhnout ho pipeline
3. Vykreslit cestu Nováček v shellu (`modules/ohg_guide.js`) jako testbed obsahu
