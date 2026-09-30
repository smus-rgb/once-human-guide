# Data files

Full dataset (186 records) lives in local project artifacts:

- `database_full.json` — complete export
- `deviations.json` (66), `weapons.json` (25), `mods.json` (18), `map_locations.json` (33)
- `once_human.db` — SQLite
- `once_human_guide_app.html` — offline SPA with embedded DB + map embeds + online update

Copy these from the project workspace or release package `OnceHumanGuide_v3.zip` into this repo root for local API:

```bash
python api_main.py
```

API will serve `/export` and `/search` from `once_human.db`.
