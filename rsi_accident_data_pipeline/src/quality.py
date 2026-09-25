
from __future__ import annotations
from .normalization import (
    candidate_is_generic,
    canonical_candidate,
    expected_region,
    region_in_geocoded_name,
    token_overlap,
)

def inside_crete(record: dict, cfg: dict) -> bool:
    try:
        x = float(record["x"])
        y = float(record["y"])
    except Exception:
        return False

    c = cfg["crete"]
    return c["west"] <= x <= c["east"] and c["south"] <= y <= c["north"]

def quality_score(record: dict, region_ok: bool, candidate_match: float) -> float:
    kind = record.get("location_kind", "")
    score = {
        "street": 0.82,
        "junction": 0.84,
        "landmark": 0.76,
        "locality": 0.67,
        "road_corridor": 0.45,
    }.get(kind, 0.35)

    if region_ok:
        score += 0.08
    else:
        score -= 0.35

    if candidate_match >= 1.0:
        score += 0.05
    elif candidate_match >= 0.5:
        score += 0.02
    elif candidate_match == 0:
        score -= 0.08

    if record.get("coordinate_method") == "corridor_midpoint":
        score -= 0.20

    return round(max(0.0, min(score, 0.98)), 2)

def validate_record(record: dict, cfg: dict) -> dict:
    out = dict(record)

    candidate = canonical_candidate(out.get("location_candidate", ""))
    out["location_candidate"] = candidate

    expected, region_source = expected_region(out)
    out["expected_region"] = expected
    out["expected_region_source"] = region_source

    region_ok = bool(expected) and region_in_geocoded_name(
        expected,
        out.get("geocoded_name", ""),
    )
    match = token_overlap(candidate, out.get("geocoded_name", ""))

    out["region_validated"] = region_ok
    out["candidate_name_overlap"] = round(match, 2)

    reasons = []

    if not inside_crete(out, cfg):
        reasons.append("coordinate_outside_crete")
    if not expected:
        reasons.append("no_expected_region")
    elif not region_ok:
        reasons.append("geocoder_region_mismatch")

    if candidate_is_generic(candidate):
        reasons.append("location_too_generic")

    if out.get("coordinate_method") == "corridor_midpoint":
        reasons.append("synthetic_corridor_midpoint")

    if out.get("location_kind") not in {"street","junction","landmark","locality"}:
        reasons.append("unsupported_location_precision")

    # Locality/candidate needs some semantic connection to the geocoder name.
    # Streets can sometimes be absent from display_name tokenization, but region
    # must still validate.
    if out.get("location_kind") == "locality" and match == 0:
        reasons.append("locality_name_not_confirmed")

    q = quality_score(out, region_ok, match)
    out["coordinate_quality"] = q

    out["coordinate_status"] = (
        "validated_approximate" if not reasons else "needs_review"
    )

    radius = cfg["quality"]["marker_radius_m"].get(
        out.get("location_kind",""),
        1500,
    )
    out["marker_radius_m"] = radius

    out["usable_for_map"] = not reasons and q >= 0.72

    # Explicit product safety rule:
    # journalism-derived geocodes must not automatically trigger driver alerts.
    out["usable_for_safety_warning"] = False
    out["verified_officially"] = False
    out["source_type"] = "journalism"

    out["quality_reasons"] = reasons
    return out
