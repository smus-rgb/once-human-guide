# Once Human Guide — Expo (Android)

Expo klient pro testování na telefonu. Zdroj je v repu (`app/`, `src/`), takže
z čistého klonu stačí nainstalovat a spustit.

## Instalace

```bash
cd expo-app
npm install
npm run sync:guide   # zkopíruje kanonický ../guide.json do src/data/
npx expo start
```

`npm start` volá `sync:guide` sám (prestart), takže po každé editaci
`guide.json` v kořeni repa stačí appku znovu spustit.

Telefon: nainstaluj **Expo Go**, naskenuj QR kód z terminálu a appka naběhne
s bundlovanou kopií průvodce (funguje i offline).

## Obrazovky

| Soubor | Obsah |
|--------|-------|
| `app/index.js` | Průvodce — vyhledávací pole (název / klíčová slova) + cesty a kroky |
| `app/step/[id].js` | Detail kroku — cíl, proč, postup, tipy, odkazy do databáze |
| `app/_layout.js` | Stack + tmavé téma (stejné tokeny jako shell v19) |

## Online režim (API + Google Drive)

Když běží API (`python ../api_main.py`) a klient má nastavenou adresu, appka
načítá průvodce z `/guide` — tedy i texty z Google Disku, pokud je nastavený
`GOOGLE_API_KEY` + `GOOGLE_DRIVE_FILE_ID` (viz README v kořeni repa).

```bash
# telefon není na localhostu — použij IP počítače v LAN
EXPO_PUBLIC_API_URL=http://192.168.1.10:8000 npx expo start
```

Bez `EXPO_PUBLIC_API_URL`, nebo když API neodpovídá, se použije bundlovaná
kopie `src/data/guide.json`.
