
from __future__ import annotations
from datetime import datetime
import math
from rapidfuzz.fuzz import ratio

from .normalization import norm, stable_event_id

def parse_date(value: str):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None

def haversine_m(a: dict, b: dict) -> float:
    lat1, lon1 = math.radians(a["y"]), math.radians(a["x"])
    lat2, lon2 = math.radians(b["y"]), math.radians(b["x"])
    dlat = lat2-lat1
    dlon = lon2-lon1
    h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 6371008.8 * 2 * math.asin(math.sqrt(h))

def same_event(a: dict, b: dict) -> bool:
    da, db = parse_date(a.get("published_at","")), parse_date(b.get("published_at",""))
    if not da or not db:
        return False

    if abs((da.date() - db.date()).days) > 2:
        return False

    distance = haversine_m(a, b)
    same_candidate = norm(a.get("location_candidate","")) == norm(b.get("location_candidate",""))
    title_similarity = ratio(norm(a.get("title","")), norm(b.get("title","")))

    return (
        (same_candidate and distance <= 1500)
        or (distance <= 250 and title_similarity >= 55)
        or (distance <= 1000 and title_similarity >= 78)
    )

def cluster(records: list[dict]) -> tuple[list[dict], list[dict]]:
    groups: list[list[dict]] = []

    for record in records:
        placed = False
        for group in groups:
            if any(same_event(record, existing) for existing in group):
                group.append(record)
                placed = True
                break
        if not placed:
            groups.append([record])

    canonical = []
    duplicate_report = []

    priority = {
        "street": 5,
        "junction": 5,
        "landmark": 4,
        "locality": 3,
        "road_corridor": 1,
    }

    for group in groups:
        urls = [r["source_url"] for r in group]
        event_id = stable_event_id(urls)

        best = max(
            group,
            key=lambda r: (
                priority.get(r.get("location_kind",""), 0),
                r.get("coordinate_quality", 0),
                len(r.get("location","")),
            ),
        )
        best = dict(best)
        best["event_id"] = event_id
        best["source_urls"] = urls
        best["source_count"] = len(group)
        canonical.append(best)

        if len(group) > 1:
            duplicate_report.append({
                "event_id": event_id,
                "count": len(group),
                "source_urls": urls,
                "titles": [r.get("title","") for r in group],
            })

    return canonical, duplicate_report
