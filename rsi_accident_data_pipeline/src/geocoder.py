
from __future__ import annotations
import json
import time
from pathlib import Path
import requests

from .normalization import canonical_candidate, region_in_geocoded_name

class StrictCreteGeocoder:
    def __init__(self, cfg: dict, root: Path):
        self.cfg = cfg
        n = cfg["nominatim"]
        self.url = n["url"]
        self.delay = max(1.05, float(n["delay_seconds"]))
        self.timeout = int(n["timeout_seconds"])
        self.cache_path = root / n["cache_file"]
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            self.cache = json.loads(self.cache_path.read_text(encoding="utf-8"))
        except Exception:
            self.cache = {}

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": cfg["crawler"]["user_agent"],
            "From": "info@roadsafetyinsights.com",
            "Accept-Language": "el,en;q=0.7",
        })
        self.last = 0.0

    def _save(self):
        self.cache_path.write_text(
            json.dumps(self.cache, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _request(self, query: str) -> list[dict]:
        if query in self.cache:
            value = self.cache[query]
            return value if isinstance(value, list) else []

        elapsed = time.time() - self.last
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)

        c = self.cfg["crete"]
        params = {
            "q": query,
            "format": "jsonv2",
            "limit": 10,
            "countrycodes": "gr",
            # Ranking hint only. We validate region ourselves.
            "viewbox": f"{c['west']},{c['north']},{c['east']},{c['south']}",
            "addressdetails": 1,
        }
        r = self.session.get(self.url, params=params, timeout=self.timeout)
        self.last = time.time()
        r.raise_for_status()
        data = r.json()

        self.cache[query] = data
        self._save()
        return data

    def _queries(self, candidate: str, kind: str, region: str) -> list[str]:
        candidate = canonical_candidate(candidate)

        if kind == "street":
            base = f"Οδός {candidate}"
        else:
            base = candidate

        raw = [
            f"{base}, {region}, Κρήτη, Ελλάδα",
            f"{base}, Περιφερειακή Ενότητα {region}, Κρήτη, Ελλάδα",
            f"{base}, Κρήτη, Ελλάδα",
        ]

        # Never fall all the way back to "candidate, Ελλάδα" in V3.
        seen = set()
        result = []
        for q in raw:
            q = " ".join(q.split()).strip(" ,")
            if q and q not in seen:
                seen.add(q)
                result.append(q)
        return result

    def repair(self, candidate: str, kind: str, expected_region: str):
        if not candidate or not expected_region:
            return None

        for query in self._queries(candidate, kind, expected_region):
            for item in self._request(query):
                display = item.get("display_name", "")
                if not region_in_geocoded_name(expected_region, display):
                    continue
                try:
                    lat = float(item["lat"])
                    lon = float(item["lon"])
                except Exception:
                    continue

                c = self.cfg["crete"]
                if not (
                    c["south"] <= lat <= c["north"]
                    and c["west"] <= lon <= c["east"]
                ):
                    continue

                return {
                    "x": lon,
                    "y": lat,
                    "geocoded_name": display,
                    "geocode_query_used": query,
                }

        return None
