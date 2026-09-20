
# RoadSafetyInsights — Crete Car Rental Lead Scraper

This tool discovers publicly listed car-rental businesses in Crete and enriches them with public business contact information for partnership outreach.

## Output
- Company name
- City / public address
- Website
- Public business email
- Public business phone
- Contact page
- Public social links
- Coordinates
- Source URL
- Lead score

## How it works
1. Discovers businesses from OpenStreetMap/Overpass using `amenity=car_rental` and `shop=car_rental`.
2. Optionally merges extra companies from `seeds.csv`.
3. Visits a small number of pages on each business website.
4. Respects `robots.txt`, rate-limits requests, and stays on the same domain.
5. Prioritizes contact/about/location/fleet pages.
6. Exports CSV and Excel.

OpenStreetMap is useful but not exhaustive, so `seeds.csv` is included for websites you want to add manually.

## Setup
Python 3.11+ recommended.

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Install:
```bash
pip install -r requirements.txt
```

Run:
```bash
python run.py
```

Outputs:
```text
output/crete_car_rentals.csv
output/crete_car_rentals.xlsx
```

Only manual seeds:
```bash
python run.py --skip-osm
```

Discovery without crawling business websites:
```bash
python run.py --skip-crawl
```

## RSI outreach workflow
After running the scraper, manually review the sheet and add:
- `outreach_status`
- `contact_person`
- `last_contacted_at`
- `response`
- `pilot_interest`
- `notes`

Good prioritization signals for your pilot are airport presence, multiple branches, tourist focus, a reachable public contact channel, and enough fleet volume to produce useful feedback.

## Responsible use
Use only for lawful business research and outreach. Respect site terms and `robots.txt`, do not bypass CAPTCHAs/authentication/access controls, and do not collect customer or non-public data. Review GDPR/ePrivacy/direct-marketing requirements before bulk outreach.

The tool is intentionally a lead-discovery utility, not an automated spam system.