# Once Human Guide

Adaptive game companion for **Once Human**  
**App 5.6.0** · Shell **v19.3** · Data `2026-10-09-v19.2-372` · Patch **3.0.7** · 373 entit · SW `ohg-2026-10-20-guide-1`

**Repo:** https://github.com/smus-rgb/once-human-guide

Spolupráce jen přes GitHub: [docs/COLLAB.md](docs/COLLAB.md). Merge do `main` jen PR. Labs větve `labs/*`.

---

## One-command install (automatic)

## Graphical installer (Start button)

```bash
# download
curl -fsSL https://raw.githubusercontent.com/smus-rgb/once-human-guide/main/install_gui.py -o install_gui.py
python3 install_gui.py
```

Windows:

```powershell
Invoke-WebRequest -Uri https://raw.githubusercontent.com/smus-rgb/once-human-guide/main/install_gui.py -OutFile install_gui.py
python install_gui.py
```

Click **START** — downloads everything, builds DB, optionally launches the app.

Needs only **Python 3.10+**.

### Windows (PowerShell)

```powershell
Invoke-WebRequest -Uri https://raw.githubusercontent.com/smus-rgb/once-human-guide/main/bootstrap.py -OutFile bootstrap.py
python bootstrap.py
cd once-human-guide-app
.\start.bat
```

### macOS / Linux

```bash
curl -fsSL https://raw.githubusercontent.com/smus-rgb/once-human-guide/main/bootstrap.py -o bootstrap.py
python3 bootstrap.py
cd once-human-guide-app
./start.sh
```

Or install directly:

```bash
curl -fsSL https://raw.githubusercontent.com/smus-rgb/once-human-guide/main/install.py -o install.py
python3 install.py --dir ~/once-human-guide-app --launch
```

Then open **http://127.0.0.1:8000/ui**

The installer automatically:
1. Downloads all app + data files from GitHub  
2. Installs `fastapi` + `uvicorn`  
3. Builds SQLite database  
4. Creates `start.sh` / `start.bat`  

### Update later

```bash
cd once-human-guide-app
python3 updater.py
```

---

## Offline (no Python)

Open `once_human_guide_v19.html` (needs `modules/`, `ohg_data.js`, `ohg_sw.js` vedle). Fallback: `once_human_guide_v18.html`.

---

## API

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/ui | App (v19 shell) |
| http://127.0.0.1:8000/docs | OpenAPI |
| http://127.0.0.1:8000/stats | Counts |
| http://127.0.0.1:8000/update/check | Update check (shell + data) |
| http://127.0.0.1:8000/audit | Data quality issues |
| http://127.0.0.1:8000/guide | Průvodce (Google Drive overlay, když je nastavený) |
| http://127.0.0.1:8000/guide.json | Průvodce — lokální obsah (offline kopie) |

---

## Průvodce hráčem (`guide.json`)

Obsah průvodce je datový soubor, ne text v HTML. Struktura: `paths[]` (cesta podle fáze hráče) → `steps[]` (krok s `goal`, `why`, `actions[]`, `tips[]`, `keywords[]`, `links[]`, `source_refs`, `verified_at`), dále `faq[]` a `glossary[]`.

- `links[].id` odkazuje na entity v packu (`weapons`, `deviations`, `scenarios`, …) — obsah se nikdy neduplikuje.
- Vyhledávání v aplikaci filtruje cesty i kroky podle názvu, cíle a klíčových slov; stejné kroky najde i globální hledání (Ctrl+K).
- Splněné kroky jdou do user layer, nikdy do `guide.json` ani do packu.
- Změna obsahu nepotřebuje rebuild: `guide.json` čte shell v19 i Expo klient.

### Texty z Google Disku

Texty průvodce lze psát přímo v dokumentu na Google Disku:

1. V Google Cloud zapni **Drive API** a vytvoř **API klíč**.
2. Dokument nasdílej jako „Anyone with the link" — API klíč ho jinak nepřečte.
3. Nastav `GOOGLE_API_KEY` a `GOOGLE_DRIVE_FILE_ID` (id z URL dokumentu).
4. `/guide` pak vrací obsah z Disku (cache 300 s), `/guide.json` zůstává offline kopie a `POST /guide/reload` vynutí obnovení. Když Disku něco chybí, aplikace mlčky použije lokální `guide.json`.

Struktura dokumentu: `# Cesta: …`, `# FAQ`, `# Slovníček`; uvnitř `## Krok: …`, řádky `Cíl:`, `Proč:`, `Čas:`, `Klíčová slova:`, `Odkazy:` (ve tvaru `tabulka/id`), odrážky `-` jako postup a `!` jako tip.
