#!/usr/bin/env bash
# Once Human Guide — start API + open UI hint
set -e
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null; then
  echo "python3 required"
  exit 1
fi

if [ ! -f once_human.db ]; then
  echo "Missing once_human.db — run: python3 install.py  or  python3 updater.py --force"
fi

python3 -m pip install -q -r requirements.txt 2>/dev/null || true

echo "Once Human Guide API"
echo "  UI:      http://127.0.0.1:8000/ui"
echo "  API:     http://127.0.0.1:8000/"
echo "  Stats:   http://127.0.0.1:8000/stats"
echo "  Search:  http://127.0.0.1:8000/search?q=socr"
echo "  Update:  http://127.0.0.1:8000/update/check"
echo "  Offline: open once_human_guide_ui_v4.html in browser"
echo ""
exec python3 -m uvicorn api_main:app --host 0.0.0.0 --port 8000
