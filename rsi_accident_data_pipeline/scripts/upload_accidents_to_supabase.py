
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "processed" / "accidents_app_ready_supabase.json"
TABLE = "accident_events"


def main():
    parser = argparse.ArgumentParser(description="Upload validated RSI accident events to Supabase")
    parser.add_argument("--file", default=str(DEFAULT_DATA))
    parser.add_argument("--batch-size", type=int, default=50)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    url = os.getenv("SUPABASE_URL", "").rstrip("/")
    secret = os.getenv("SUPABASE_SECRET_KEY", "").strip()
    if not url:
        raise SystemExit("Missing SUPABASE_URL")
    if not secret:
        raise SystemExit("Missing SUPABASE_SECRET_KEY")

    data_file = Path(args.file)
    if not data_file.is_absolute():
        data_file = ROOT / data_file
    rows = json.loads(data_file.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise SystemExit("Input must be a JSON array")
    if len([r.get("id") for r in rows]) != len(set(r.get("id") for r in rows)):
        raise SystemExit("Duplicate IDs found. Run verify_dataset.py first.")

    print(f"File: {data_file}")
    print(f"Rows: {len(rows)}")
    print(f"Destination: {url}/rest/v1/{TABLE}")
    if args.dry_run:
        print("Dry run complete. No data uploaded.")
        return

    endpoint = f"{url}/rest/v1/{TABLE}"
    # New Supabase sb_secret_* keys are API keys, not JWTs. Send them only
    # through the apikey header.
    headers = {
        "apikey": secret,
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=minimal",
    }

    batch_size = max(1, args.batch_size)
    for start in range(0, len(rows), batch_size):
        batch = rows[start:start+batch_size]
        r = requests.post(
            endpoint,
            headers=headers,
            params={"on_conflict": "id"},
            json=batch,
            timeout=60,
        )
        if not r.ok:
            print("\nUPLOAD FAILED")
            print("HTTP:", r.status_code)
            print(r.text)
            r.raise_for_status()
        print(f"Uploaded {min(start+batch_size, len(rows))}/{len(rows)}")

    verify = requests.get(
        endpoint,
        headers={"apikey": secret, "Prefer": "count=exact", "Range": "0-0"},
        params={"select": "id"},
        timeout=30,
    )
    verify.raise_for_status()
    print("\nUpload finished.")
    print("Supabase content-range:", verify.headers.get("content-range", ""))


if __name__ == "__main__":
    main()
