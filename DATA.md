# Once Human Guide — Data

**version:** `2026-10-01-v19-372`  
**app:** 5.3.1  
**patch_target:** 3.0.7 live · Isles of Abyss prep  

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

## Install / update

```bash
python3 install.py --from-github
python3 updater.py
```

Updater **assembles** `database_full.json` from module JSON when the monolithic file is not present, then rebuilds `once_human.db`.

Full embedded SPA + SQLite dump: see **OnceHumanGuide_Complete.zip** in project artifacts.

## Schema notes (5.3.1)

- `locations` keep `x` and `y` in SQLite (map pins).
- `recipes.effect` is stored, not dropped.
- Any field outside the core schema is kept in `extra` JSON.
- Rebuild: `python3 updater.py --force` then `GET /integrity`.
