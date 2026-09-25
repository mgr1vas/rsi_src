# RoadSafetyInsights — Crete Accident Data Pipeline

Internal repository for collecting, validating, reviewing, deduplicating, and
storing **traffic-accident locations in Crete derived from journalistic reports**.

## Current phase

**Private Supabase database setup only.** We are not connecting this dataset to
the Flutter app yet.

## Current snapshot

| Metric | Result |
| --- | ---: |
| Raw candidate records | 186 |
| Validated before deduplication | 111 |
| Canonical app-ready/database records | **85** |
| Rejected / manual review | 75 |
| Duplicate groups detected | 16 |
| Missing dates in canonical data | 0 |
| Approved for live safety warnings | **0** |

The canonical file for Supabase is:

```text
data/processed/accidents_app_ready_supabase.json
```

Eight publication timestamps with day/month ambiguity were cross-checked and
corrected; the audit is in `data/qa/date_corrections_audit.json`.

## Critical rule

These X/Y values are **journalism-derived approximate locations**, not official
police crash coordinates.

Every current canonical record must remain:

```json
{
  "source_type": "journalism",
  "verified_officially": false,
  "usable_for_map": true,
  "usable_for_safety_warning": false
}
```

Do not use these rows to automatically trigger live driver warnings.

## Repository structure

```text
rsi-accident-data-pipeline/
├── README.md
├── CONTRIBUTING.md
├── SECURITY.md
├── LICENSE.md
├── requirements.txt
├── config.yaml
├── run.py
├── data/
│   ├── raw/accidents_xy_v2.json
│   ├── processed/accidents_app_ready_supabase.json
│   └── qa/
│       ├── quality_report.json
│       ├── rejected_review.json
│       ├── duplicate_groups.json
│       └── date_corrections_audit.json
├── src/                     # validation / repair / dedupe pipeline
├── scripts/
│   ├── verify_dataset.py
│   ├── upload_accidents_to_supabase.py
│   ├── first_push.ps1
│   └── first_push.sh
├── sql/001_create_accident_events.sql
├── docs/
│   ├── DATA_QUALITY.md
│   └── MORNING_HANDOFF.md
└── .github/workflows/validate-data.yml
```

## Team quick start

### 1. Install dependencies

Windows:

```powershell
py -m pip install --user -r requirements.txt
```

### 2. Validate the canonical dataset

```powershell
py scripts/verify_dataset.py
```

Expected:

```text
records: 85
unique ids: 85
future dates: 0
safety-warning enabled: 0
errors: 0
Dataset validation PASSED.
```

GitHub Actions runs the same validation automatically on pushes and pull requests.

## Supabase — current task

### 1. Create the table

In Supabase **SQL Editor**, run:

```text
sql/001_create_accident_events.sql
```

This creates the private `public.accident_events` table. RLS is enabled and no
public/mobile read policy is created yet.

### 2. Set credentials locally

PowerShell:

```powershell
$env:SUPABASE_URL="https://YOUR_PROJECT_REF.supabase.co"
$env:SUPABASE_SECRET_KEY="sb_secret_YOUR_REAL_SECRET"
```

Never commit either a real secret key or a `.env` file.

### 3. Dry run

```powershell
py scripts/upload_accidents_to_supabase.py --dry-run
```

### 4. Upload

```powershell
py scripts/upload_accidents_to_supabase.py
```

The uploader uses an upsert on `id`, so rerunning it updates matching IDs instead
of deliberately adding duplicate primary keys.

### 5. Verify in Supabase

```sql
select count(*) from public.accident_events;
```

Expected:

```text
85
```

## Data files

### `data/raw/accidents_xy_v2.json`

Historical working geocoded dataset. Contains known ambiguous/wrong results.
**Do not upload it directly to Supabase.**

### `data/processed/accidents_app_ready_supabase.json`

Current canonical dataset. This is the only JSON intended for `accident_events`.

### `data/qa/rejected_review.json`

Records intentionally excluded because of issues such as region mismatch, generic
location, synthetic corridor midpoint, insufficient precision, or failed locality
confirmation.

### `data/qa/duplicate_groups.json`

Audit trail for multiple articles believed to describe the same accident.

### `data/qa/quality_report.json`

Summary of the validation run.

### `data/qa/date_corrections_audit.json`

Audit trail for the eight corrected publication timestamps.

## Running the pipeline again

To regenerate candidate outputs from the raw V2 dataset:

```powershell
py run.py build --input data/raw/accidents_xy_v2.json
```

Generated files go to `output/` and are ignored by Git. Review them before
replacing the canonical file in `data/processed/`.

The date parser in this repository includes a fix for ISO-8601 dates so it does
not swap month/day when NeaKriti supplies machine-readable timestamps.

## First GitHub push

Create an **empty private repository** in the RoadSafetyInsights organization,
for example:

```text
rsi-accident-data-pipeline
```

Do not initialize the GitHub repo with another README, because this package already
contains one.

Then either run manually:

```powershell
git init
git add .
git commit -m "Initial Crete accident data pipeline"
git branch -M main
git remote add origin https://github.com/RoadSafetyInsights/rsi-accident-data-pipeline.git
git push -u origin main
```

or use:

```powershell
.\scriptsirst_push.ps1 -RepoUrl "https://github.com/RoadSafetyInsights/rsi-accident-data-pipeline.git"
```

## Security

- Never commit the Supabase secret key.
- Do not put the secret key in Flutter.
- Preserve source URLs/provenance.
- Prefer fewer defensible coordinates over many weak coordinates.
- Journalism-derived coordinates are not official crash points.

## Future architecture

```text
approved public sources
        ↓
scraper / Apify
        ↓
validation + dedupe
        ↓
manual-review queue
        ↓
Supabase/Postgres
        ↓
RSI backend/API
        ↓
Flutter app
```

n8n can later orchestrate scheduling, scraper jobs, QA notifications and ingestion.
For now the focus is a clean, auditable database.
