# Morning handoff

## Status

The NeaKriti Crete accident pipeline has moved from raw scraping/geocoding to a
conservative validated dataset for database storage.

Current V3 result:

```text
186 candidate records
111 passed validation before deduplication
85 app-ready after deduplication
75 rejected / manual review
16 duplicate groups
0 app-ready records enabled for live safety warnings
```

Eight publication timestamps with day/month ambiguity were cross-checked and
corrected in the canonical Supabase dataset.

## Canonical data

Upload only:

```text
data/processed/accidents_app_ready_supabase.json
```

Do not upload `data/raw/accidents_xy_v2.json` as production data.

## Important interpretation

The 85 rows are validated **approximate reported accident locations**. They are
not exact crash coordinates and are not approved for automatic driver warnings.

Every current event remains:

```text
source_type = journalism
verified_officially = false
usable_for_map = true
usable_for_safety_warning = false
```

## What to do this morning

1. Read `README.md` and `docs/DATA_QUALITY.md`.
2. Run `py scripts/verify_dataset.py`.
3. Create the private Supabase table using `sql/001_create_accident_events.sql`.
4. Set `SUPABASE_URL` and `SUPABASE_SECRET_KEY` locally.
5. Run `py scripts/upload_accidents_to_supabase.py`.
6. Confirm the table contains 85 rows.

No Flutter integration is required in this phase.
