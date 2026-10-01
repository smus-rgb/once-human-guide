# Changelog

## 5.3.0 / 2026-10-01-v19-379

- App: `/ui` now serves `once_human_guide_v18.html` (the v4 file was never in the repo, so the endpoint 404'd).
- Database: version strings unified (`database_full.json` was still `v5-complete` while the shell claimed `v18-372`).
- Database: `tech` module (7 records) for the 28 Sep 2026 tech-tree overhaul — Survival, Production, Combat, Building, reverse engineering, Terrain Modifier.
- System: rebuild keeps `user_favorites`, `user_progress`, `builds`, `map_markers` and writes `audit_log`.
- System: name indexes + SQL `LIKE` search instead of loading every row into Python.
- API: `GET/POST/DELETE /favorites`.

## 5.2.0 / 2026-09-30-v18-372

- Adaptive shell v18, 372 curated records, installer/updater pull the v18 pack.
