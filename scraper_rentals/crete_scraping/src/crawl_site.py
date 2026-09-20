
from __future__ import annotations
import time
from collections import defaultdict
from typing import Any
from urllib import robotparser
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup
from .utils import absolutize, domain_key, extract_emails, extract_phones, normalize_url, same_site, social_kind

class SiteCrawler:
    def __init__(self, config: dict[str, Any]):
        self.cfg = config["crawl"]
        self.client = httpx.Client(
            timeout=self.cfg["timeout_seconds"],
            follow_redirects=True,
            headers={"User-Agent": self.cfg["user_agent"]},
        )
        self.last_fetch = defaultdict(lambda: 0.0)
        self.robots_cache = {}

    def close(self):
        self.client.close()

    def _allowed(self, url: str) -> bool:
        if not self.cfg.get("respect_robots_txt", True):
            return True
        p = urlparse(url)
        root = f"{p.scheme}://{p.netloc}"
        if root not in self.robots_cache:
            rp = robotparser.RobotFileParser()
            rp.set_url(root + "/robots.txt")
            try:
                rp.read()
            except Exception:
                rp.parse([])
            self.robots_cache[root] = rp
        return self.robots_cache[root].can_fetch(self.cfg["user_agent"], url)

    def _rate_limit(self, url: str):
        domain = domain_key(url)
        delay = float(self.cfg["per_domain_delay_seconds"])
        elapsed = time.time() - self.last_fetch[domain]
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self.last_fetch[domain] = time.time()

    def _fetch(self, url: str) -> str:
        if not self._allowed(url):
            return ""
        self._rate_limit(url)
        r = self.client.get(url)
        r.raise_for_status()
        if "text/html" not in (r.headers.get("content-type") or "").lower():
            return ""
        raw = r.content[:int(self.cfg["max_response_bytes"])]
        return raw.decode(r.encoding or "utf-8", errors="replace")

    def crawl(self, start_url: str) -> dict[str, Any]:
        start_url = normalize_url(start_url)
        if not start_url:
            return {}
        queue, visited = [start_url], set()
        emails, phones = set(), set()
        socials = defaultdict(set)
        contact_pages = []

        while queue and len(visited) < int(self.cfg["max_pages_per_site"]):
            url = queue.pop(0)
            if url in visited:
                continue
            visited.add(url)
            try:
                html = self._fetch(url)
            except Exception:
                continue
            if not html:
                continue

            soup = BeautifulSoup(html, "lxml")
            visible = " ".join(soup.stripped_strings)
            emails.update(extract_emails(html + "\n" + visible))
            phones.update(extract_phones(visible))

            if any(k in url.lower() for k in ("contact", "επικοινων")):
                contact_pages.append(url)

            for a in soup.find_all("a", href=True):
                href = absolutize(url, a.get("href", ""))
                if not href:
                    continue
                kind = social_kind(href)
                if kind:
                    socials[kind].add(href)
                    continue
                if same_site(start_url, href):
                    haystack = (" ".join(a.stripped_strings) + " " + href).lower()
                    if any(k in haystack for k in self.cfg["page_keywords"]) and href not in visited and href not in queue:
                        queue.append(href)

        return {
            "scraped_email": "; ".join(sorted(emails)),
            "scraped_phone": "; ".join(sorted(phones)),
            "contact_page": contact_pages[0] if contact_pages else "",
            "facebook": "; ".join(sorted(socials.get("facebook", set()))),
            "instagram": "; ".join(sorted(socials.get("instagram", set()))),
            "linkedin": "; ".join(sorted(socials.get("linkedin", set()))),
            "tiktok": "; ".join(sorted(socials.get("tiktok", set()))),
            "youtube": "; ".join(sorted(socials.get("youtube", set()))),
            "pages_crawled": len(visited),
        }
