# Once Human Guide

Adaptive game companion for **Once Human**  
**App 5.2** · Data `2026-09-30-v5-complete` · Patch **3.0.7**

**Repo:** https://github.com/smus-rgb/once-human-guide

---

## Graphical installer (button START)

### Windows (PowerShell)

```powershell
Invoke-WebRequest -Uri https://raw.githubusercontent.com/smus-rgb/once-human-guide/main/install_gui.py -OutFile install_gui.py
python install_gui.py
```

### macOS / Linux

```bash
curl -fsSL https://raw.githubusercontent.com/smus-rgb/once-human-guide/main/install_gui.py -o install_gui.py
python3 install_gui.py
```

1. Opens a window **ONCE HUMAN GUIDE**  
2. Click **▶ START**  
3. Wait for download + database  
4. App opens at http://127.0.0.1:8000/ui  

*(Needs Python 3.10+ with tkinter. Linux: `sudo apt install python3-tk`)*

---

## Terminal installer

```bash
curl -fsSL https://raw.githubusercontent.com/smus-rgb/once-human-guide/main/bootstrap.py -o bootstrap.py
python3 bootstrap.py
cd once-human-guide-app && ./start.sh
```

---

## Update

```bash
cd once-human-guide-app
python3 updater.py
```

## Offline

Open `once_human_guide_ui_v4.html` in a browser (from Complete zip).
