#!/usr/bin/env python3
"""Validate module JSON before a pack bump. Pack files are not rewritten."""
from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
MODULES = [
    "deviations.json", "weapons.json", "armor.json", "mods.json", "bosses.json",
    "map_locations.json", "recipes.json", "materials.json", "scenarios.json",
    "quests.json", "events.json", "creatures.json", "npcs.json", "plants.json",
    "fish.json", "animals.json", "flowers.json",
]

def main() -> int:
    errors = []
    total = 0
    for name in MODULES:
        path = BASE / name
        if not path.exists():
            errors.append(f"missing {name}")
            continue
        raw = json.loads(path.read_text(encoding="utf-8"))
        rows = raw if isinstance(raw, list) else []
        seen = set()
        for row in rows:
            total += 1
            rid = row.get("id")
            if not rid:
                errors.append(f"{name}: missing id on {row.get('name')}")
                continue
            if rid in seen:
                errors.append(f"{name}: duplicate id {rid}")
            seen.add(rid)
            if not (row.get("name") or "").strip():
                errors.append(f"{name}: empty name {rid}")
    print(json.dumps({"ok": not errors, "records": total, "errors": errors}, ensure_ascii=False))
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
