# ONCE HUMAN GUIDE — UI SYSTEM ARCHITECTURE

**Verze:** 4.0 · Autonomous UI Architect output  
**Datum:** 2026-09-30  
**Cíl:** Jeden adaptivní, modulární UI engine pro phone → tablet → desktop → ultrawide

---

## PHASE 1 — Analýza systému

### Účel
Digitální průvodce hrou Once Human: databázový terminál přeživších — items, builds, mapa, questy, AI guide, progress. Offline-first, online sync, personalizace.

### Typy uživatelů
| Persona | Primární potřeby | Frekvence |
|---------|------------------|-----------|
| Nový hráč | Tutorial path, beginner deviations, early weapons | High search |
| Mid-game farmer | Resources, recipes, silo mods, territory deviations | Map + filter |
| Endgame / boss runner | Builds, mods, weaknesses, routes | Compare + AI |
| PvP | Loadouts, mobility, map control | Builds + map |
| Casual companion | Quick lookup, AI questions | Search-first |

### Nejčastější informace (priorita 1 klik)
1. Globální search (cokoliv)
2. Mapa (kde je X)
3. Item / weapon detail
4. AI „co na bosse / co na craft“
5. Oblíbené + progress

### Sekundární
Scenarios detail, herbalist genetics, fishing tables, flower grafting, animal breeding, NPC dialogue, event timers.

### Informační vztahy (propojení DB)
```
SCENARIO → locations → bosses → drops → items/mods
ITEM ← recipes ← materials ← locations
WEAPON → mods → builds → armor sets → deviations
QUEST → NPC → location → rewards
CREATURE → drops → weaknesses → recommended builds
```

### Offline / Sync
```
LOCAL IndexedDB/SQLite  →  CACHE  →  SYNC QUEUE  →  REMOTE API
Boot: load local snapshot → background version check → optional /export merge
```

---

## PHASE 2 — Informační architektura (moduly)

| Modul | Route | Priority | UI pattern |
|-------|-------|----------|------------|
| Dashboard / Command Center | `/` | P0 | Widgets grid |
| Global Search | `/search` | P0 | Command palette + results |
| Map Workspace | `/map` | P0 | Full canvas + layers |
| Database Hub | `/db` | P0 | Category rails + cards/table |
| Items | `/db/items` | P0 | Cards → detail |
| Weapons | `/db/weapons` | P0 | Cards + compare |
| Armor / Mods | `/db/armor`, `/db/mods` | P0 | Cards |
| Deviations | `/db/deviations` | P0 | Filter chips + cards |
| Builds | `/builds` | P0 | Slot planner |
| Recipes / Crafting | `/craft` | P1 | Tree + chain |
| Bestiary | `/bestiary` | P1 | Cards + weaknesses |
| Quests | `/quests` | P1 | Timeline / checklist |
| Scenarios | `/scenarios` | P1 | Phase timeline |
| Events | `/events` | P1 | Timer cards |
| NPC | `/npc` | P2 | Profiles |
| Herbalist / Plants | `/plants` | P2 | Table + map pins |
| Fishing | `/fishing` | P2 | Table |
| Animals | `/animals` | P2 | Cards |
| Flowers / Grafting | `/grafting` | P2 | Combo matrix |
| AI Guide | `/ai` | P0 | Chat + entity links |
| Progress / Profile | `/progress` | P1 | Checklist + stats |
| Settings | `/settings` | P1 | Forms |

---

## PHASE 3 — Navigation

### Mobile (≤679px)
- Bottom nav: **Search · Map · Home · Builds · More**
- FAB: AI Guide
- Details: full-screen or bottom sheet
- Filters: bottom sheet chips

### Tablet (680–1100px)
- Left compact rail (icons + labels on expand)
- Main content
- Optional right detail drawer

### Desktop (≥1101px)
- Permanent sidebar (icons + text)
- Main workspace
- Right context inspector (persistent when selection exists)
- Command palette: `Ctrl/Cmd+K`

### Contextual navigation
- Context stack + breadcrumbs: `Map → Boss → Drop → Recipe`
- Recently viewed (session)
- Back restores previous workspace state

---

## PHASE 4 — Responsive layout engine

```
inputs: width, height, orientation, pointer:coarse|fine, hover, safe-area, reduced-motion
→ deviceClass: phone | phablet | tablet | laptop | desktop | ultrawide
→ navMode: bottom | rail | sidebar
→ columns: 1 | 2 | 3 | 4+
→ density: compact | comfortable
→ detailMode: sheet | drawer | panel
→ tableMode: cards | hybrid | table
```

Breakpoints (soft, space-based):
- phone: max-width 679
- tablet: 680–1100
- desktop: 1101–1599
- ultrawide: 1600+

---

## PHASE 5 — Design tokens (tactical terminal)

```
--bg: #05070a
--surface: #0c1016
--surface-2: #121820
--surface-3: #182028
--border: #2a3540
--border-dim: #1c252e
--text: #e6edf3
--text-dim: #8b98a5
--cyan: #5ce1ff
--cyan-dim: rgba(92,225,255,.12)
--amber: #e8b84a
--red: #ff5c6c
--green: #7ddea0
--purple: #a78bfa
--scanline: rgba(92,225,255,.03)
--glow-cyan: 0 0 20px rgba(92,225,255,.15)
--radius-sm: 6px
--radius: 10px
--radius-lg: 14px
--font: "IBM Plex Sans", "Segoe UI", system-ui, sans-serif
--font-mono: "IBM Plex Mono", ui-monospace, monospace
--space-1..8: 4/8/12/16/20/24/32/48
--z-nav: 30; --z-drawer: 50; --z-modal: 60; --z-toast: 70
```

Visual language: charcoal panels, thin technical borders, cyan accent, amber warning, subtle grid/scanline, no SaaS pastels.

---

## PHASE 6 — Component library (core)

AppShell · Sidebar · BottomNav · TopBar · SearchBar · GlobalSearchOverlay  
ItemCard · EntityCard · FilterChips · DetailPanel · DataTable  
MapCanvas · MapLayerToggle · MapMarker · BottomSheet · Drawer  
AIChat · RecommendationBlock · ProgressBar · Timeline  
FavoriteToggle · Breadcrumbs · Toast · EmptyState · LoadingSkeleton · BootScreen

---

## PHASE 7–12 — Screen patterns

### Dashboard (Command Center)
Modular widgets: Player status · Scenario · Active goals · Map snapshot · Recent · Favorites · AI prompt · Sync status  
Desktop: draggable/resizable widget grid (v2). Mobile: stacked priority cards.

### Global Search
Command palette overlay; results grouped by category; entity open → detail panel.

### Map Workspace
Desktop: layers left | map center | detail right  
Mobile: map full + floating search/filter + bottom sheet detail  
Layers: settlements, silos, bosses, POI, resources, quests, custom

### Database screens
Filter chips + search; phone = cards; desktop = optional table; selection opens inspector.

### AI Guide
Chat stream; responses with clickable entity chips linking to DB objects; optional online retrieval.

---

## PHASE 13–14 — Profile & Offline

Local keys: favorites, progress flags, owned/want, notes, build slots, recent, apiBase, dbCache  
Sync: GET /version → if newer GET /export → merge local cache

---

## PHASE 15–17 — Device optimization

Mobile: touch 44px, bottom nav, sheets, one-column  
Tablet: rail + 2-col content  
Desktop: sidebar + inspector + command palette + multi-column

---

## PHASE 18–22 — Quality gates

UX: search ≤2 taps, back path always, empty/loading/error states  
A11y: focus rings, aria labels, reduced motion, contrast  
Perf: virtualized lists when >50, lazy map iframes, memoized filters  
No duplicate nav systems; one AdaptiveShell

---

## Implementační stack (v4)

1. **Primary deliverable:** single-file adaptive SPA (`once_human_guide_ui_v4.html`) — production-ready UI engine  
2. Existing API + JSON DB as data layer  
3. React/Expo continue as parallel clients sharing data model  

