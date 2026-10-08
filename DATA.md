# Once Human Guide — Data

**version:** `2026-10-08-v19.2-372`  
**app:** 5.5.0  
**shell:** 19.2  
**patch_target:** 3.0.7 live · Isles of Abyss prep  
**records:** 372 (pack unchanged in this release)

## Modules on GitHub (module JSON)

| File | Role |
|------|------|
| deviations.json | Combat / Territory / Crafting deviations |
| weapons.json | Named weapons |
| armor.json | Armor sets |
| mods.json | Weapon & armor mods |
| bosses.json | Silo / monolith / raid bosses |
| map_locations.json | Regions, silos, hubs |
| recipes.json | Food, ammo, structures |
| materials.json | Craft mats & currencies |
| scenarios.json | Manibus, Winter, SCP, RaidZone, Abyss… |
| quests.json | Main / side / silo quests |
| events.json | Golden Autumn, Prime War, Abyss reservation |
| creatures.json | Bestiary |
| npcs.json | Vendors & quest NPCs |
| plants / fish / animals / flowers | Gatherables |
| search_aliases.json | Czech/EN search aliases (system, not pack) |

## Database

`python3 db_build.py` builds `once_human.db`:

- one table per module + indexes on name/type/rarity
- `entities` catalog and FTS5 (`unicode61 remove_diacritics 2`)
- `links` from recipe ingredients and boss locations
- `search_aliases` for Czech queries (`deviace`, `zbraň`, `recept`…)

User layer (favorites, inventory, builds) is never written by the builder.

## Install / update

```bash
python3 install.py --from-github
python3 updater.py
```

Updater assembles `database_full.json` from module JSON when the monolithic file is not present, then rebuilds `once_human.db`.
