# Once Human Guide — Complete App

Adaptive tactical UI + SQLite/JSON database for **Once Human**  
**App 5.0.0** · **Data `2026-09-30-v5-complete`** · **372 records** · patch **3.0.7**

**GitHub:** https://github.com/smus-rgb/once-human-guide

---

## Quick install

### From this folder (local)

```bash
python3 install.py --dir ~/once-human-guide-app
cd ~/once-human-guide-app
./start.sh
```

### From GitHub only

```bash
curl -fsSL https://raw.githubusercontent.com/smus-rgb/once-human-guide/main/install.py -o install.py
python3 install.py --from-github --dir ~/once-human-guide-app
cd ~/once-human-guide-app && ./start.sh
```

### Offline UI (no Python)

Open `once_human_guide_ui_v4.html` in a browser.

---

## Auto-updater

```bash
python3 updater.py           # download newer data from GitHub
python3 updater.py --check   # only check versions
python3 updater.py --force   # re-download everything
./update.sh
```

API:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/update/check` | GET | Local vs GitHub version |
| `/update/run` | POST | Run updater (`?force=true`) |

---

## API

```bash
pip install -r requirements.txt
python api_main.py
# or ./start.sh
```

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/ui | Full SPA |
| http://127.0.0.1:8000/stats | Record counts |
| http://127.0.0.1:8000/search?q=socr | Global search |
| http://127.0.0.1:8000/export | Full JSON |
| http://127.0.0.1:8000/docs | OpenAPI |
| http://127.0.0.1:8000/update/check | Update status |

---

## Database (372)

| Module | # |
|--------|--:|
| deviations | 71 |
| locations | 42 |
| mods | 48 |
| weapons | 38 |
| recipes | 26 |
| materials | 24 |
| creatures | 20 |
| quests | 18 |
| armor | 18 |
| bosses | 16 |
| npcs | 11 |
| scenarios | 10 |
| plants / animals | 7 / 7 |
| fish / flowers / events | 5 / 6 / 5 |

---

## Files

| File | Role |
|------|------|
| `install.py` | One-shot installer |
| `updater.py` | GitHub auto-updater + SQLite rebuild |
| `version.json` | Version manifest for updates |
| `once_human_guide_ui_v4.html` | Offline SPA |
| `once_human.db` | SQLite (built by install/updater) |
| `database_full.json` | Master data |
| `api_main.py` | FastAPI server |
| `start.sh` | Launch API |
