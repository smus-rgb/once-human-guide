# Changelog

## 5.3.1 / shell 19.0 — 2026-10-01

- API `/ui` umí nabootovat shell: servíruje `/ohg_data.js`, `/ohg_sw.js`, `/version.json` a `/modules`
- SQLite už nezahazuje `locations.x/y` ani `recipes.effect`; neznámá pole jdou do `extra`
- Indexy + FTS `search_fts`; vyhledávání v SQL (limit/offset), ne full scan v Pythonu
- `GET /integrity` porovná počty JSON vs SQLite a verzi
- `database_full.json` sjednocen na `2026-10-01-v19-372` (372 entit)
- SW cache `ohg-v19-308`

## 5.3.0 / shell 19.0 — 2026-10-01

- Tenký host `once_human_guide_v19.html`; runtime v `modules/ohg_runtime.js`
- Mapa: region filtr, vrstvy, tile placeholder (`modules/ohg_map.js`)
- Build Planner: validace slotů proti packu, export `ohg-build.json`
- Pack kanál: `version.json` → diff do Agent queue; schválení jen overlay, pack se nemění
- API `/ui` servíruje v19, `/update/check` vrací shell+data
- SW cache `ohg-v19-307`
- v18 zůstává offline fallback

## 5.2.0 / shell 18.0 — 2026-10-01 archive

- Kanonický snapshot `OnceHumanGuide_v18.0.0_complete.zip` (shell / data / tools / docs)
- Legacy zip přesunuty do `archive/legacy/`
- GitHub `main` sync: v18 shell + `ohg_data.js` + `ohg_sw.js` + spec; release `v18.0.0`

## 5.0.0 — 2026-09-30

- Installer, updater, FastAPI 5.x
- 372 records, dual JSON + SQLite
- UI v4 offline HTML
