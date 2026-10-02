# Showcase Archive — Weapons, Armor & Scenario Maps

Cinematic presentation cards for **every** weapon and armor piece in Once Human  
(all rarities: Legendary / Epic / Rare / Common) + interactive scenario maps.

## Visual Style (mandatory)
- Same tone as the SOCR – Last Valor reference card: dark cinematic background, red/cyan glow, gold legendary frame, orthographic + detail views, lore + exact stats.
- Each item gets its **own tailored image** (hero + details) matching the real in-game model as closely as possible.
- Armor cards **always** include full world / set bonuses (1pc → 4pc / 6pc).

## Data Source
Primary accurate database: [oncehumandb.com](https://www.oncehumandb.com/)  
Cross-checked with in-game tooltips and community verified numbers (2026 patch 3.0.x).

## Interactive Maps (Scenarios)
Source: [oncehuman.th.gl](https://oncehuman.th.gl) (The Hidden Gaming Lair)

**Required behaviour (identical to source):**
- At **0 % zoom** the entire map fits exactly inside the frame.
- Map **cannot be panned** until the user zooms in.
- After zoom-in, free panning + further zoom is enabled.
- Correct map asset per scenario (Manibus, Way of Winter, Endless Dream, Deviation SCP, Prismverse, Evolution’s Call, Isles of Abyss when available).

## Card Structure
```
showcase/
  weapons/
    socr-the-last-valor.md
    aws-338-bullseye.md
    ...
  armor/
    lonewolf-set.md
    shelterer-set.md
    ...
  maps/
    manibus.md
    way-of-winter.md
    ...
```

Each `.md` contains:
- Full lore
- Exact stats table
- Weapon Features / Set Bonuses
- Detail view labels
- Image generation prompt (for consistent style)
- Tags & meta synergies

## Progress
- [x] Card format defined
- [x] SOCR – The Last Valor (AR, Shrapnel)
- [x] AWS.338 – Bullseye (Sniper)
- [x] Lonewolf Set (full 1–4pc bonuses)
- [ ] Remaining Legendary weapons
- [ ] Epic / Rare / Common weapons
- [ ] All armor sets + individual pieces
- [ ] Scenario map configs with correct bounds & zoom lock
