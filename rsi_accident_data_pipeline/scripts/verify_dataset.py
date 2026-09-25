
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "accidents_app_ready_supabase.json"
CRETE = {"west": 23.30, "south": 34.70, "east": 26.50, "north": 35.85}
REQUIRED = {
    "id", "x", "y", "published_at", "region", "location_candidate",
    "coordinate_status", "coordinate_quality", "coordinate_source",
    "source_type", "source", "source_url", "verified_officially",
    "usable_for_map", "usable_for_safety_warning",
}


def main():
    rows = json.loads(DATA.read_text(encoding="utf-8"))
    errors = []
    ids = [r.get("id") for r in rows]
    now = datetime.now(timezone.utc)
    future = 0
    warning_enabled = 0

    for i, row in enumerate(rows):
        missing = sorted(REQUIRED - set(row))
        if missing:
            errors.append(f"row {i}: missing {missing}")
        if not row.get("id"):
            errors.append(f"row {i}: empty id")

        try:
            x, y = float(row["x"]), float(row["y"])
            if not (CRETE["west"] <= x <= CRETE["east"] and CRETE["south"] <= y <= CRETE["north"]):
                errors.append(f"{row.get('id')}: coordinate outside Crete bounds")
        except Exception:
            errors.append(f"{row.get('id')}: invalid x/y")

        try:
            dt = datetime.fromisoformat(row["published_at"].replace("Z", "+00:00"))
            if dt.astimezone(timezone.utc) > now:
                future += 1
                errors.append(f"{row.get('id')}: future published_at {row['published_at']}")
        except Exception:
            errors.append(f"{row.get('id')}: invalid published_at")

        if row.get("source_type") == "journalism":
            if row.get("verified_officially") is not False:
                errors.append(f"{row.get('id')}: journalism marked officially verified")
            if row.get("usable_for_safety_warning"):
                warning_enabled += 1
                errors.append(f"{row.get('id')}: journalism enabled for safety warning")

        if row.get("usable_for_map") is not True:
            errors.append(f"{row.get('id')}: processed row is not usable_for_map")
        if not row.get("source_url"):
            errors.append(f"{row.get('id')}: missing source_url")

    if len(ids) != len(set(ids)):
        errors.append(f"duplicate ids: {len(ids)-len(set(ids))}")

    print(f"records: {len(rows)}")
    print(f"unique ids: {len(set(ids))}")
    print(f"future dates: {future}")
    print(f"safety-warning enabled: {warning_enabled}")
    print(f"errors: {len(errors)}")

    if errors:
        print("\nVALIDATION ERRORS")
        for error in errors[:100]:
            print("-", error)
        raise SystemExit(1)

    print("\nDataset validation PASSED.")


if __name__ == "__main__":
    main()
