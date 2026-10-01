# Spolupráce — Emergent Labs

Jediný kanál je GitHub. Žádné ad-hoc kopírování souborů.

## Model

| Kanál | Účel |
|-------|------|
| Issues | bugy, data gaps, požadavky Labs |
| PR | jediný způsob merge do `main` |
| `labs/*` | experimentální větve (fork nebo branch) |
| CODEOWNERS | `@smus-rgb` na vše; Labs jen review |
| Releases | binární truth pro installer |

## Pravidla

1. Pracovat na forku nebo větvi `labs/*`. Přímý push do `main` ne.
2. Data změny jen jako PR s diffem proti `*.json`. Pack `ohg_data.js` se regeneruje z JSON, ne ručně.
3. UI experimenty v `labs/ui-*`. Do shellu až po review.
4. PR musí: nezlomit offline HTML (`once_human_guide_v19.html` + `modules/` + `ohg_data.js`), nezlomit count entit (teď 372), aktualizovat CHANGELOG.
5. User layer (favorites, inventory, builds, queue) nikdy nemění pack.
6. Checklist je v `.github/PULL_REQUEST_TEMPLATE.md`.

## Pozvánka

Collaborator se přidává ručně v GitHub → Settings → Collaborators. GitHub login Emergent Labs zatím není v projektu — bez něj nejde issue assign ani CODEOWNERS řádek.
