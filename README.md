# Once Human Guide v3

**Repo:** https://github.com/smus-rgb/once-human-guide

Adaptive companion pro **Once Human** — web SPA, React, Expo (mobil) + online API.

## Rychlý start

| Klient | Příkaz |
|--------|--------|
| **HTML SPA** | Otevři `once_human_guide_app.html` (z release / workspace) |
| **API** | `python api_main.py` → http://localhost:8000 |
| **React** | `cd react-app && npm i && npm run dev` |
| **Expo** | `cd expo-app && npm i && npx expo start` |

## Novinky v3

### Databáze (186 záznamů)
- 66 deviations · 25 zbraní · 12 armor · 18 mods · 33 lokací · 16 receptů

### Mapa embed
- **Lokální body** (filtry)
- **THGL** iframe → https://oncehuman.th.gl
- **MapGenie** iframe → mapgenie.io/once-human

### Online vyhledávání a aktualizace
- `GET /version` — kontrola verze dat
- `GET /search?q=` — online fuzzy search
- `GET /export` — plný JSON snapshot pro update klienta
- V SPA: tlačítka **Update** a **Online ⌕**, nastavení API URL

### Expo mobil
- Složka `expo-app/` — iOS / Android / web
- Offline DB + online update/search přes stejné API

## API endpointy

```
GET /version
GET /stats
GET /deviations?q=&type=
GET /weapons?q=
GET /armor?q=
GET /mods?q=
GET /locations
GET /bosses
GET /recipes
GET /search?q=&limit=
GET /export
GET /maps
```

## Data v repozitáři

- `api_main.py`, `weapons.json`, `bosses.json`, `materials.json`
- Další JSON + SPA HTML + SQLite: viz `DATA.md` a balíček `OnceHumanGuide_v3.zip` z workspace

## Licence

Community fan project — data z veřejných wiki / community sources. Once Human © NetEase / Starry Studio.
