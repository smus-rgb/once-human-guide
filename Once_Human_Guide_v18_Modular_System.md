# Once Human Guide — v18 Modular System

**Verze:** 18.0 · AdaptiveShell + ModuleHost  
**Shell:** `once_human_guide_v18.html` + `ohg_data.js` + `ohg_sw.js`  
**Datum:** 2026-09-30  
**Data:** 372 entit · patch 3.0.7

Plnohodnotný databázový companion — jedna společná architektura pro telefon, tablet, PC i ultrawide. Data a komponenty jsou sdílené; každý breakpoint má vlastní informační hierarchii a ovládání.

## Architektura

| Vrstva | Role |
|--------|------|
| Pack | `OHG_DATA` / `OHG_META` — 372 entit, 17 kategorií |
| Cache | `ohg_sw.js` · `ohg-v18-307` |
| Pack kanál | local pack first → SW precache → volitelný `version.json` |
| User | `ohg_user` — fav, inv, progress, builds, notes, queue, offline |
| Host | ModuleHost · hash `#modul[/id]` |
| Shell | phone / tablet / desktop / ultrawide |

## Adaptivní UI (ne pouhé zmenšení PC)

| Breakpoint | Layout | Hierarchie |
|------------|--------|------------|
| **Telefon** | Bottom nav: Home / Search / Map / Database / More | Jeden sloupec, detaily jako bottom sheet |
| **Tablet** | Úzký sidebar + 2 sloupce | Seznam + detail; kontext na vyžádání |
| **PC** | Permanent sidebar + main + context panel | Navigace vždy vidět, inspector vpravo |
| **Ultrawide** | Sidebar + list column + main + context | Čtyři sloupce, tabulky a mapové vrstvy |

Lock layoutu: AUTO / phone / tablet / desktop / ultrawide (Settings).

## 18 modulů

1. **Home / Dashboard** — pack status, rychlé cesty, poslední výběr  
2. **AI Guide** — retrieval nad packem + fronta návrhů  
3. **Globální Search** — Ctrl+K command palette přes všechny entity  
4. **Databáze** — Items, Weapons, Armor, Mods, Deviations, Enemies/Bestiary, Animals, Plants, Resources, Locations  
5. **Interactive Map** — piny z `locations`, vrstvy, sheet na telefonu  
6. **Crafting & Recipes** — recepty z packu, checklist  
7. **Build Planner** — Doomeris/Anestic buckety, 12 meta šablon, power score  
8. **Scenario Guide** — scénáře / fáze  
9. **Progress Tracker** — checklisty + export  
10. **Herbalist / Cooking** — rostliny + recepty  
11. **Flower Grafting** — dva rodiče → výsledek  
12. **Animal system** — habitat, taming, produkty  
13. **Events & activities**  
14. **Favorites / Collections**  
15. **Personal inventory** — qty +/−  
16. **Offline mode** — SW cache + local pack  
17. **AI Agent** — review queue, žádný zápis do packu bez schválení  
18. **Settings + synchronizace** — layout lock, import/export user layer  

## Sdílené komponenty

- `item` / `card` / `chip` / `slot` / `listPane` / `entityDetail`  
- `search()` nad `allEntities()`  
- `go(route, entity)` + hash routing  
- user layer isolovaný od packu  

## Soubory

| Soubor | Úloha |
|--------|--------|
| `once_human_guide_v18.html` | AdaptiveShell + 18 modulů |
| `ohg_data.js` | Pack 372 |
| `ohg_sw.js` | Offline cache ohg-v18-307 |
| `Once_Human_Guide_v18_Modular_System.md` | Spec |

## Další krok (v19) — hotovo 2026-10-01

Tenký host `once_human_guide_v19.html` načítá `modules/ohg_runtime.js`, `ohg_map.js`, `ohg_builds.js`, `ohg_pack_channel.js`. v18 zůstává offline fallback. Pack 372 beze změny.
