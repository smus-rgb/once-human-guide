# Scenario Interactive Maps

Source of truth: **https://oncehuman.th.gl**

## Required Behaviour (must match source page)
1. At **0 % / min zoom** the **entire map** fits exactly inside the viewport/frame.
2. Panning is **disabled** until the user zooms in at least one step.
3. After zoom-in → free pan + further zoom enabled.
4. Use the correct map tile/asset for each scenario.

## Scenarios & Map Links
| Scenario                        | Map URL / Notes |
|---------------------------------|-----------------|
| Manibus / Manibus (Novice)      | oncehuman.th.gl (Manibus map) |
| The Way of Winter               | oncehuman.th.gl + gmtreks.com/oncehuman/map/way-of-winter |
| Endless Dream                   | oncehuman.th.gl |
| Deviation: Survive, Capture, Preserve | oncehuman.th.gl (Deviation Secure) |
| Prismverse’s Clash              | oncehuman.th.gl |
| Evolution’s Call                | oncehuman.th.gl |
| Isles of Abyss (upcoming)       | TBD – ocean map |

## Implementation Notes for UI
- Leaflet / MapLibre / custom canvas: set `maxBounds` = full map bounds, `minZoom` so that full map is visible, disable drag until zoom > minZoom.
- Or embed the THGL map with matching CSS constraints.
