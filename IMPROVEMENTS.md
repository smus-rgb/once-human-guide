# Plánovaná vylepšení Once Human Guide

Tento soubor shrnuje směr vylepšení aplikace, systému a databáze.

## Databáze (db_build.py)
- Extra sloupec pro neznámá pole z packu
- Více vazeb (ingredient, drop, located_at, reward, source)
- Tabulka data_issues pro audit
- FTS5 s unicode61 remove_diacritics=2
- Indexy na type, rarity, region, slot

## Systém
- API čte verzi z version.json
- Endpointy /integrity, /audit, /facets
- Filtrování v list endpointech
- User layer v once_human_user.db (favorites, notes, progress)
- Zabezpečení /update/run tokenem

## Aplikace (shell v19)
- modules/ohg_quality.js — panel kvality
- Search bez diakritiky
- Badge DB status
- Export/import user dat

Všechny změny respektují: pack je kanonický, user layer odděleně, merge jen PR.
