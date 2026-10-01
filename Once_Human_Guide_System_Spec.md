# Once Human Guide — systémová specifikace UI/UX

## 1. Cíl
Jedna aplikace, tři hustoty rozhraní: Android telefon, mobil/tablet a PC. Jeden datový model a komponentový systém; pouze layout, hustota informací a navigace se mění podle dostupné šířky, výšky, vstupu a orientace.

## 2. Breakpointy
- 0–679 px: Phone UI — bottom navigation, single column, touch targets min. 44 px.
- 680–1000 px: Mobile/Tablet — compact rail, 2 columns, větší mapové a databázové panely.
- 1001+ px: PC — full sidebar, 3–5 columns, tabulky, klávesové zkratky, split view.
- Runtime režim AUTO je výchozí. Manuální preview režim slouží pouze pro testování.

## 3. Hlavní navigace
Dashboard / Databáze / Mapa / Buildy / Deviations / Crafting / AI Guide / Progress / Discord / Nastavení.

### Phone
Bottom nav: Home, Search, Map, Build, More. Sekundární moduly jsou uvnitř More.

### Tablet
Left compact rail + contextual bottom actions.

### PC
Permanentní sidebar + top search + contextual inspector panel.

## 4. Core obrazovky
1. Dashboard — stav synchronizace, rychlé akce, doporučené moduly, poslední změny.
2. Universal Search — fuzzy search, filtry, kategorie, historie.
3. Database — Items, Weapons, Armor, Mods, Deviations, Recipes, Materials, NPC, Bosses, Locations.
4. Map — vrstvy, markery, route planner, vlastní body, resource tracking.
5. Build Planner — loadout, cradle, mods, armor, synergy, stat comparison.
6. Crafting — recept → požadované suroviny → stanice → nákupní seznam.
7. Progress — checklist a completion tracking.
8. AI Guide — chat nad databází, citace zdrojů, datum ověření, confidence flag pouze jako technický údaj, nikoliv jako marketingové tvrzení.
9. Settings — účet, cache, sync, jazyk, jednotky, vzhled, privacy, notifications.

## 5. Datová architektura
- `items`
- `weapons`
- `armor`
- `mods`
- `deviations`
- `recipes`
- `materials`
- `locations`
- `bosses`
- `quests`
- `builds`
- `user_progress`
- `favorites`
- `map_markers`
- `sources`
- `data_versions`

Každý záznam má stabilní ID, název, lokalizace, tagy, verzi dat, updated_at a source_refs.

## 6. AI Agent
Pipeline: user query → intent detection → database retrieval → source/version check → answer composer → source references → optional action.

AI nesmí tiše měnit databázi. Návrhy změn jdou do review queue. Každá automatická aktualizace má audit log.

## 7. Adaptive UI engine
Vstupy:
- viewport width/height
- orientation
- pointer type / coarse vs fine
- touch capability
- safe-area insets
- reduced motion preference
- light/dark host preference

Výstup:
`deviceClass`, `navMode`, `density`, `columns`, `drawerMode`, `mapControls`, `tableMode`.

## 8. Design tokens
Background: #07090C
Panels: #10151B / #151C23
Borders: #27323C
Text: #E8EDF2
Muted: #8D9AA6
Accent: cyan #63E6FF
Success: green #9DF58C
Warning: amber #FFD166
Danger: red #FF6575

## 9. UX zásady
- žádné důležité akce pouze hoverem;
- touch target min. 44×44 px;
- search dostupný z každé hlavní obrazovky;
- hluboké databázové obrazovky podporují split view na PC;
- offline cache pro základní databázi;
- změny dat jsou verzované;
- uživatelská data jsou oddělena od globální databáze;
- mapové a databázové filtry se ukládají per uživatel.

## 10. Doporučený technický stack
Frontend: React/Next.js nebo React Native/Expo podle cílové platformy.
State: Zustand.
Local data: SQLite/IndexedDB podle platformy.
API: REST/GraphQL podle backendu.
AI: agent service s retrieval vrstvou.
Maps: vlastní mapový renderer + tile/cache strategie.
Auth/sync: token-based session + per-user data layer.

## 11. Komponentový systém
AppShell, AdaptiveSidebar, BottomNav, CommandSearch, StatCard, EntityCard, DataTable, FilterBar, MapLayerPanel, DetailDrawer, BuildSlot, RecipeTree, ProgressRing, AIChat, SourceBadge, SyncStatus, VersionBadge, EmptyState, ErrorState, OfflineBanner.

## 12. Stavové režimy
Loading / Ready / Offline / Syncing / Conflict / Error / Empty / PermissionDenied.
Každý stav musí mít vlastní UI; aplikace nesmí působit jako rozbitá při ztrátě připojení.
