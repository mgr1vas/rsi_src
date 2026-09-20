
from __future__ import annotations
import argparse, csv, re
from pathlib import Path
from typing import Any
import pandas as pd
import yaml
from .crawl_site import SiteCrawler
from .discover_osm import discover_from_osm
from .utils import domain_key, normalize_phone, normalize_url

ROOT = Path(__file__).resolve().parents[1]

def load_config(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return yaml.safe_load(p.read_text(encoding="utf-8"))

def load_seeds(path: str) -> list[dict[str, Any]]:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    if not p.exists():
        return []
    rows = []
    with p.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if any((v or "").strip() for v in row.values()):
                rows.append({
                    "company_name": (row.get("company_name") or "").strip(),
                    "website": normalize_url(row.get("website") or ""),
                    "city": (row.get("city") or "").strip(),
                    "address": "", "phone": "", "email": "",
                    "latitude": "", "longitude": "",
                    "source": "Manual seed", "source_url": "",
                    "notes": (row.get("notes") or "").strip(),
                })
    return rows

def normalize_name(name: str) -> str:
    return re.sub(r"[^a-z0-9α-ω]+", "", (name or "").lower())

def dedupe(leads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged, by_domain, by_name_city = [], {}, {}
    for lead in leads:
        lead = dict(lead)
        lead["website"] = normalize_url(lead.get("website", ""))
        if lead.get("phone"):
            lead["phone"] = normalize_phone(lead["phone"])
        d = domain_key(lead["website"])
        nc = (normalize_name(lead.get("company_name", "")), normalize_name(lead.get("city", "")))
        idx = by_domain.get(d) if d else None
        if idx is None and nc[0]:
            idx = by_name_city.get(nc)
        if idx is None:
            idx = len(merged)
            merged.append(lead)
            if d: by_domain[d] = idx
            if nc[0]: by_name_city[nc] = idx
        else:
            current = merged[idx]
            for k, v in lead.items():
                if not current.get(k) and v not in ("", None):
                    current[k] = v
    return merged

def enrich(leads, config):
    crawler = SiteCrawler(config)
    try:
        for i, lead in enumerate(leads, 1):
            if not lead.get("website"):
                continue
            print(f"[{i}/{len(leads)}] Crawling {lead.get('company_name') or lead['website']}")
            details = crawler.crawl(lead["website"])
            lead.update(details)
            if not lead.get("email") and details.get("scraped_email"):
                lead["email"] = details["scraped_email"].split(";")[0].strip()
            if not lead.get("phone") and details.get("scraped_phone"):
                lead["phone"] = details["scraped_phone"].split(";")[0].strip()
    finally:
        crawler.close()
    return leads

def score_lead(row):
    score = 0
    if row.get("website"): score += 2
    if row.get("email") or row.get("scraped_email"): score += 3
    if row.get("phone") or row.get("scraped_phone"): score += 2
    if row.get("contact_page"): score += 1
    if row.get("instagram") or row.get("facebook") or row.get("linkedin"): score += 1
    if row.get("city"): score += 1
    return score

def export(leads, config):
    for lead in leads:
        lead["lead_score"] = score_lead(lead)
    df = pd.DataFrame(leads)
    if not df.empty:
        df = df.sort_values(["lead_score", "company_name"], ascending=[False, True])
    csv_path = ROOT / config["output"]["csv"]
    xlsx_path = ROOT / config["output"]["xlsx"]
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    df.to_excel(xlsx_path, index=False)
    print(f"Saved {len(df)} leads to:")
    print(csv_path)
    print(xlsx_path)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--seeds", default="seeds.csv")
    ap.add_argument("--skip-osm", action="store_true")
    ap.add_argument("--skip-crawl", action="store_true")
    args = ap.parse_args()

    config = load_config(args.config)
    leads = load_seeds(args.seeds)
    if not args.skip_osm:
        print("Discovering Crete car rentals from OpenStreetMap/Overpass...")
        leads.extend(discover_from_osm(config))
    leads = dedupe(leads)
    print(f"Discovered {len(leads)} unique candidate businesses.")
    if not args.skip_crawl:
        leads = enrich(leads, config)
    export(leads, config)

if __name__ == "__main__":
    main()
