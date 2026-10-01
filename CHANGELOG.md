# Changelog

## 5.4.0 — 2026-10-01

- `/ui` teď servuje `ohg_data.js` a `modules/*.js` (shell se na API opravdu spustí)
- SQLite rebuild: indexy na `name` + virtual table `search_fts` (FTS5)
- `GET /health`, `GET /integrity` (JSON vs SQLite, duplicitní id, prázdné name)
- `/search` používá FTS5, fallback LIKE
- v19 badge DB z `/integrity`
- pack zůstává 372 entit

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

## 5.2.0 / shell 18.0 — 2026-09-30

- AdaptiveShell v18 + ModuleHost + hash routing
- Pack `ohg_data.js` 372 entit, SW cache `ohg-v18-307`
- Installer/updater stahují `once_human_guide_v18.html`, `ohg_data.js`, `ohg_sw.js`
- Sjednocené verze: `version.json` app 5.2.0, data `2026-09-30-v18-372`
- Hotfix: Home badge App 18.0 (místo 17.0)

## 5.0.0 — 2026-09-30

- Installer, updater, FastAPI 5.x
- 372 records, dual JSON + SQLite
- UI v4 offline HTML
