# Once Human Guide

Adaptive UI terminal + curated game database for **Once Human**.

**Repo:** https://github.com/smus-rgb/once-human-guide  
**Data version:** `2026-09-30-v4-3.0.7-plus-abyss-prep`  
**Patch target:** 3.0.7 live · Isles of Abyss prep (Oct 21–22 2026)

## Quick start

1. Open `once_human_guide_ui_v4.html` in a browser (offline-capable SPA).
2. Or run API: `python api_main.py` (serves JSON + search).

## Database counts (247 records)

| Module | Count |
|--------|------:|
| animals | 7 |
| armor | 18 |
| bosses | 8 |
| creatures | 6 |
| deviations | 70 |
| events | 5 |
| fish | 3 |
| flowers | 3 |
| locations | 33 |
| materials | 8 |
| mods | 18 |
| npcs | 4 |
| plants | 4 |
| quests | 6 |
| recipes | 16 |
| scenarios | 10 |
| weapons | 28 |

## Modules in UI

Command · Search · Map · DB · Scenarios · Quests · Events · Bestiary · NPC · Deviations · Builds · Craft · Plants · Fishing · Animals · Grafting · AI · Progress

## Structure

- `once_human_guide_ui_v4.html` — production adaptive SPA
- `database_full.json` / category `*.json` — seed data
- `api_main.py` — data API skeleton
- `react-app/` · `expo-app/` — client scaffolds
- `Once_Human_Guide_UI_Architecture.md` — UI system design

## Notes

- Version **3.0.8** is not published yet; next major content is **Isles of Abyss**.
- Catalog is curated core, not a full dump of every in-game spawn/skin.
