# AGENTS.md — provozní poznámky pro tento repozitář

Tyto poznámky doplňují manifesty (`requirements.txt`, `expo-app/package.json`) o věci, které
z kódu nejsou na první pohled vidět. Nic, co už říkají manifesty, tu není zopakované.

## Co je aplikace

- `api_main.py` — FastAPI backend (port 8000). Servíruje REST API i statické UI.
- `once_human_guide_v19.html` + `modules/*.js` — tenký webový shell (UI je na cestě `/ui`).
  Moduly se nahrávají za běhu jako nehashované soubory, takže úpravy v `modules/` jsou živé.
- `nginx.base44.conf` — jediný veřejný vstup. Na host portu 3000 mapuje `/` → `/ui`
  a zbytek (API, `/guide`, `/guide.json`, statické soubory) → `api:8000`.
- `expo-app/` — nativní Android klient (Expo). Sdílí designové tokeny se shellem v19.
  Data průvodce do klienta bundluje `expo-app/scripts/sync-guide.mjs` z `guide.json` v kořeni.

## Databáze

- SQLite `once_human.db` (v `.gitignore`) se **generuje**, není součástí checkoutu.
- V sandboxu to dělá jednorázová compose služba `db` (`python db_build.py`), která doběhne
  a skončí; `api` na ni čeká přes `depends_on: condition: service_completed_successfully`.
  Když `api` hlásí chybějící tabulky, znamená to, že `db` nedoběhla (`docker compose logs db`).

## Obsah průvodce a Google Disk

- Kanonický obsah průvodce je `guide.json` v kořeni repa. Entity zůstávají v packu
  (`ohg_data.js` / JSON moduly), `guide.json` na ně odkazuje přes `links[].id` — needuplikovat.
- Google Disk je **volitelný overlay**, ne podmínka běhu:
  - `GOOGLE_API_KEY` — klíč s povoleným Drive API.
  - `GOOGLE_DRIVE_FILE_ID` — id nasdíleného Google dokumentu nebo JSON souboru s texty.
- Bez těchto dvou proměnných aplikace startuje normálně a servíruje lokální `guide.json`.
  Pozná se to podle `meta.source == "local"` v odpovědi `/guide.json` (resp. `/guide`).
  S klíči se zdroj přepne na Drive a nový obsah se dá vynutit přes `/guide/reload`.
- Oba klíče jsou `requiredAtBoot: false` — nejsou potřeba k bootu a v sandboxu je klidně
  přeskoč. Aplikace pak ukazuje lokální obsah.

## Sandbox / vývojové prostředí

- Spuštění: `docker compose -f docker-compose.base44.yml up -d --build`
- Služby běží z klonovaného zdrojového kódu (bind mount, `uvicorn --reload`), nikdy
  z předpřipraveného produkčního image — úpravy jsou proto živé bez rebuildu.
- Service worker `ohg_sw.js` obsahuje precache seznam souborů. Ten je nutné držet
  v souladu s verzováním, jinak offline režim servíruje staré moduly.

## Jak ověřit, že běh je v pořádku

1. `docker compose -f docker-compose.base44.yml ps` — `api` i `web` musí být `healthy`.
2. `curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/` → `200`.
3. `curl -s http://localhost:3000/guide.json` → `meta.source` je `local` (bez Google klíčů).
4. `curl -s http://localhost:3000/guide` → stav průvodce (cesty, kroky, splněno).
5. V UI: otevřít `/ui`, kliknout v levém menu na **Guide** — v pravém panelu se musí objevit
   „GUIDE · LOCAL", počet cest/kroků a karty cest s kroky.
