# Once Human Guide

Adaptive game companion for **Once Human**  
**App 5.1** · Data `2026-09-30-v5-complete` · Patch **3.0.7**

**Repo:** https://github.com/smus-rgb/once-human-guide

---

## One-command install (automatic)

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

Open `once_human_guide_ui_v4.html` from the Complete zip in a browser.

---

## API

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/ui | App |
| http://127.0.0.1:8000/docs | OpenAPI |
| http://127.0.0.1:8000/stats | Counts |
| http://127.0.0.1:8000/update/check | Update check |
