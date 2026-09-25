
from __future__ import annotations
import json
import re
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser


class ArticleMetadataFetcher:
    def __init__(self, cfg: dict):
        self.timeout = int(cfg["crawler"]["timeout_seconds"])
        self.delay = float(cfg["crawler"]["delay_seconds"])
        self.last = 0.0
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": cfg["crawler"]["user_agent"],
            "Accept-Language": "el,en;q=0.7",
        })

    def _get(self, url: str) -> str:
        elapsed = time.time() - self.last
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        r = self.session.get(url, timeout=self.timeout)
        self.last = time.time()
        r.raise_for_status()
        return r.text

    @staticmethod
    def _to_iso(value: str) -> str:
        """Parse machine-readable dates without swapping month/day.

        NeaKriti JSON-LD/meta dates are commonly ISO-8601. V3 originally used
        dayfirst=True for every input, which can turn 2026-09-12 into 2026-12-09.
        ISO-looking values are now parsed with isoparse first.
        """
        if not value:
            return ""
        value = str(value).strip()
        try:
            if re.match(r"^\d{4}-\d{2}-\d{2}", value):
                return date_parser.isoparse(value).isoformat()
            return date_parser.parse(value, dayfirst=True).isoformat()
        except Exception:
            return ""

    def published_at(self, url: str) -> str:
        html = self._get(url)
        soup = BeautifulSoup(html, "lxml")

        # 1. JSON-LD
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                obj = json.loads(script.get_text(strip=True))
            except Exception:
                continue
            items = obj if isinstance(obj, list) else [obj]
            if isinstance(obj, dict) and isinstance(obj.get("@graph"), list):
                items += obj["@graph"]
            for item in items:
                if isinstance(item, dict) and item.get("datePublished"):
                    parsed = self._to_iso(str(item["datePublished"]))
                    if parsed:
                        return parsed

        # 2. Standard article metadata
        for attrs in (
            {"property": "article:published_time"},
            {"name": "datePublished"},
            {"name": "date"},
        ):
            tag = soup.find("meta", attrs=attrs)
            if tag and tag.get("content"):
                parsed = self._to_iso(tag["content"])
                if parsed:
                    return parsed

        # 3. <time datetime=...>
        time_tag = soup.find("time", datetime=True)
        if time_tag:
            parsed = self._to_iso(time_tag["datetime"])
            if parsed:
                return parsed

        # 4. Visible NeaKriti format DD.MM.YY HH:MM
        visible = " ".join(soup.stripped_strings)
        match = re.search(
            r"\b(\d{2})\.(\d{2})\.(\d{2})\s+(\d{2}):(\d{2})\b",
            visible,
        )
        if match:
            day, month, yy, hour, minute = map(int, match.groups())
            year = 2000 + yy
            return datetime(year, month, day, hour, minute).isoformat()

        return ""
