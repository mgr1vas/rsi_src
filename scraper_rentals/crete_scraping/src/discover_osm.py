
from __future__ import annotations
from typing import Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from .utils import normalize_url

def build_overpass_query(bbox: list[float], tags: list[str]) -> str:
    south, west, north, east = bbox
    clauses = "\n".join(f'nwr{tag}({south},{west},{north},{east});' for tag in tags)
    return f"""[out:json][timeout:60];
(
{clauses}
);
out center tags;
"""

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def discover_from_osm(config: dict[str, Any]) -> list[dict[str, Any]]:
    dcfg = config["discovery"]
    query = build_overpass_query(dcfg["crete_bbox"], dcfg["osm_tags"])
    headers = {"User-Agent": config["crawl"]["user_agent"]}
    with httpx.Client(timeout=75, follow_redirects=True, headers=headers) as client:
        r = client.post(dcfg["overpass_url"], data={"data": query})
        r.raise_for_status()
        payload = r.json()

    leads = []
    for el in payload.get("elements", []):
        tags = el.get("tags", {})
        center = el.get("center", {})
        address = " ".join(x for x in [
            tags.get("addr:street", ""),
            tags.get("addr:housenumber", ""),
            tags.get("addr:city", ""),
            tags.get("addr:postcode", ""),
        ] if x).strip()
        leads.append({
            "company_name": tags.get("name", "").strip(),
            "website": normalize_url(tags.get("website") or tags.get("contact:website") or tags.get("url") or ""),
            "city": tags.get("addr:city", "").strip(),
            "address": address,
            "phone": (tags.get("phone") or tags.get("contact:phone") or "").strip(),
            "email": (tags.get("email") or tags.get("contact:email") or "").strip().lower(),
            "latitude": el.get("lat", center.get("lat")),
            "longitude": el.get("lon", center.get("lon")),
            "source": "OpenStreetMap",
            "source_url": f"https://www.openstreetmap.org/{el['type']}/{el['id']}",
            "notes": "",
        })
    return leads
