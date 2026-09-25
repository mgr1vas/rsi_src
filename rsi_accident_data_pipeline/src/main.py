
from __future__ import annotations
import argparse
import json
from pathlib import Path
import yaml

from .article_metadata import ArticleMetadataFetcher
from .dedupe import cluster
from .geocoder import StrictCreteGeocoder
from .normalization import stable_record_id
from .quality import validate_record

ROOT = Path(__file__).resolve().parents[1]


def load_cfg(path: str):
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def load_json(path: str):
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return json.loads(p.read_text(encoding="utf-8"))


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def build(cfg: dict, input_path: str, skip_dates: bool):
    rows = load_json(input_path)
    metadata = ArticleMetadataFetcher(cfg)
    geocoder = StrictCreteGeocoder(cfg, ROOT)
    validated, rejected = [], []

    for idx, raw in enumerate(rows, 1):
        record = dict(raw)
        record["id"] = record.get("id") or stable_record_id(record["source_url"])

        if not record.get("date") and not record.get("published_at") and not skip_dates:
            try:
                record["published_at"] = metadata.published_at(record["source_url"])
            except Exception as exc:
                record["published_at"] = ""
                record["date_fetch_error"] = type(exc).__name__
        else:
            record["published_at"] = record.get("published_at") or record.get("date", "")

        checked = validate_record(record, cfg)

        if (
            cfg["quality"]["repair_region_mismatches"]
            and "geocoder_region_mismatch" in checked["quality_reasons"]
            and checked.get("expected_region")
        ):
            print(f"[{idx}/{len(rows)}] repairing {checked.get('location_candidate')} -> {checked['expected_region']}")
            try:
                repaired = geocoder.repair(
                    checked.get("location_candidate", ""),
                    checked.get("location_kind", ""),
                    checked["expected_region"],
                )
            except Exception as exc:
                repaired = None
                checked["repair_error"] = type(exc).__name__

            if repaired:
                checked.update(repaired)
                checked["coordinate_method"] = "strict_region_regeocode"
                checked = validate_record(checked, cfg)

        (validated if checked["usable_for_map"] else rejected).append(checked)

    if cfg["quality"]["deduplicate"]:
        app_ready, duplicate_groups = cluster(validated)
    else:
        app_ready, duplicate_groups = validated, []

    compact = []
    for r in app_ready:
        compact.append({
            "id": r["event_id"],
            "x": r["x"], "y": r["y"],
            "published_at": r.get("published_at", ""),
            "region": r.get("expected_region") or r.get("region", ""),
            "title": r.get("title", ""),
            "location_text": r.get("location", ""),
            "location_candidate": r.get("location_candidate", ""),
            "location_kind": r.get("location_kind", ""),
            "coordinate_status": r.get("coordinate_status", ""),
            "coordinate_quality": r.get("coordinate_quality", 0),
            "marker_radius_m": r.get("marker_radius_m"),
            "coordinate_source": r.get("coordinate_source", ""),
            "source_type": "journalism",
            "source": r.get("source", "NeaKriti"),
            "source_url": r.get("source_url", ""),
            "source_urls": r.get("source_urls", [r.get("source_url", "")]),
            "source_count": r.get("source_count", 1),
            "verified_officially": False,
            "usable_for_map": True,
            "usable_for_safety_warning": False,
        })

    outcfg = cfg["output"]
    write_json(ROOT / outcfg["all_validated"], validated)
    write_json(ROOT / outcfg["app_ready"], compact)
    write_json(ROOT / outcfg["rejected"], rejected)
    write_json(ROOT / outcfg["duplicate_report"], duplicate_groups)

    report = {
        "input_records": len(rows),
        "validated_before_dedupe": len(validated),
        "app_ready_after_dedupe": len(compact),
        "rejected_or_review": len(rejected),
        "duplicate_groups": len(duplicate_groups),
        "region_mismatch_remaining": sum(
            "geocoder_region_mismatch" in r.get("quality_reasons", []) for r in rejected
        ),
        "missing_dates_app_ready": sum(not r.get("published_at") for r in compact),
        "safety_warning_records": sum(bool(r.get("usable_for_safety_warning")) for r in compact),
    }
    write_json(ROOT / outcfg["quality_report"], report)

    print("\nBUILD COMPLETE")
    for k, v in report.items():
        print(f"{k:28}: {v}")
    print(f"\nCandidate output: {ROOT / outcfg['app_ready']}")
    print("Review it before replacing data/processed/accidents_app_ready_supabase.json.")


def main():
    ap = argparse.ArgumentParser(description="RSI Crete accident validation pipeline")
    ap.add_argument("--config", default="config.yaml")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("build")
    p.add_argument("--input", default="data/raw/accidents_xy_v2.json")
    p.add_argument("--skip-dates", action="store_true")
    args = ap.parse_args()
    cfg = load_cfg(args.config)
    if args.cmd == "build":
        build(cfg, args.input, args.skip_dates)


if __name__ == "__main__":
    main()
