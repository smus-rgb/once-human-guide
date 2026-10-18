# Next steps after v19.2 audit

Based on open PRs and system spec:

## Database
- Expand links generation for drops, locations, rewards, sources (beyond recipes).
- Ensure FTS and data_issues are robust.

## API
- Add optional filters (type, rarity, region, slot) to list endpoints.
- Separate user.db for favorites/progress that survives pack rebuild.
- Token-protect /update/run.

## Application
- Enhance shell search for Czech (diacritics-insensitive).
- Integrate quality panel fully.
- Better offline support.

All changes keep pack as canonical (372 entities). User data separate.

Current PR #18 implements the audit foundation. Merge recommended, then continue.
