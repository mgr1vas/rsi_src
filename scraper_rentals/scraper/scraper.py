```python
#!/usr/bin/env python3
# Used ChatGPT Model 6 Astra

import argparse
import csv
import random
import re
import sys
import time
from collections import deque
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Iterable
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from ddgs import DDGS


# Configuration

DEFAULT_OUTPUT = "greece_car_rentals.csv"
DEFAULT_MIN_DELAY = 1.5
DEFAULT_MAX_DELAY = 4.0
DEFAULT_TIMEOUT = 15
DEFAULT_RETRIES = 2
DEFAULT_SEARCH_RESULTS = 10
DEFAULT_MAX_SEARCH_QUERIES = 60
DEFAULT_MAX_PAGES_PER_DOMAIN = 4


# Search terms used to identify car rental businesses

BUSINESS_KEYWORDS = [
    "car rental",
    "rent a car",
    "car hire",
    "rental cars",
    "ενοικίαση αυτοκινήτων",
    "ενοικιάσεις αυτοκινήτων",
]


# Greek locations used for nationwide discovery

GREECE_LOCATIONS = [
    "Athens",
    "Piraeus",
    "Thessaloniki",
    "Patras",
    "Larissa",
    "Heraklion",
    "Chania",
    "Rethymno",
    "Agios Nikolaos",
    "Rhodes",
    "Kos",
    "Corfu",
    "Zakynthos",
    "Kefalonia",
    "Lefkada",
    "Mykonos",
    "Santorini",
    "Naxos",
    "Paros",
    "Ios",
    "Milos",
    "Skiathos",
    "Skopelos",
    "Kavala",
    "Volos",
    "Ioannina",
    "Kalamata",
    "Sparta",
    "Nafplio",
    "Tripoli",
    "Chalkida",
    "Alexandroupoli",
    "Komotini",
    "Xanthi",
    "Serres",
    "Katerini",
    "Chios",
    "Samos",
    "Lesvos",
    "Mytilene",
    "Limnos",
    "Karpathos",
    "Kasos",
    "Astypalaia",
    "Tinos",
    "Syros",
]


# Generic nationwide search queries

GENERIC_QUERIES = [
    '"car rental" Greece',
    '"rent a car" Greece',
    '"car hire" Greece',
    '"car rental Greece"',
    '"rent a car Greece"',
    '"ενοικίαση αυτοκινήτων" Ελλάδα',
    '"ενοικιάσεις αυτοκινήτων" Ελλάδα',
    '"rental cars" Greece',
    '"car rental companies" Greece',
    '"car rental services" Greece',
]


# User agents used for HTTP requests

USER_AGENTS = [
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) "
        "Gecko/20100101 Firefox/142.0"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/18.6 Safari/605.1.15"
    ),
    (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36"
    ),
]


# Rental business data model

@dataclass
class RentalRecord:
    business_name: str = ""
    business_type: str = ""
    city: str = ""
    region: str = ""
    country: str = "Greece"
    website: str = ""
    source_url: str = ""
    phone: str = ""
    email: str = ""
    car_models: str = ""
    price_text: str = ""
    description: str = ""
    discovered_from_query: str = ""
    search_result_title: str = ""
    scraped_at: str = ""
    confidence: str = ""


# Cache robots.txt responses to avoid requesting them repeatedly

ROBOTS_CACHE = {}


# Utility functions

def normalize_whitespace(value: str) -> str:
    if not value:
        return ""

    return re.sub(r"\s+", " ", value).strip()


def safe_url(url: str) -> str:
    if not url:
        return ""

    url = url.strip()

    if not re.match(r"^https?://", url, re.I):
        url = "https://" + url

    try:
        parsed = urlparse(url)

        clean_path = parsed.path.rstrip("/") or "/"

        return urlunparse(
            (
                parsed.scheme.lower(),
                parsed.netloc.lower(),
                clean_path,
                "",
                "",
                "",
            )
        )
    except Exception:
        return ""


def base_domain(url: str) -> str:
    try:
        host = urlparse(url).netloc.lower().split(":")[0]

        if host.startswith("www."):
            host = host[4:]

        return host
    except Exception:
        return ""


def random_delay(min_delay: float, max_delay: float) -> None:
    if max_delay < min_delay:
        min_delay, max_delay = max_delay, min_delay

    time.sleep(
        random.uniform(
            min_delay,
            max_delay,
        )
    )


def clean_text(text: str, max_length: int = 2000) -> str:
    text = normalize_whitespace(text)
    return text[:max_length]


def looks_like_rental_page(text: str) -> bool:
    lowered = text.lower()

    return any(
        keyword.lower() in lowered
        for keyword in BUSINESS_KEYWORDS
    )


def extract_emails(text: str) -> list[str]:
    pattern = r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}"

    emails = re.findall(
        pattern,
        text,
        flags=re.IGNORECASE,
    )

    cleaned = set()

    for email in emails:
        email = email.strip(
            ".,;:()[]{}<>\"'"
        )

        if "example.com" in email.lower():
            continue

        cleaned.add(email.lower())

    return sorted(cleaned)


def extract_phones(text: str) -> list[str]:
    patterns = [
        r"\+\d[\d\s().-]{7,}\d",
        r"\b2\d{9}\b",
        r"\b69\d{8}\b",
    ]

    phones = []

    for pattern in patterns:
        phones.extend(
            re.findall(
                pattern,
                text,
            )
        )

    cleaned = []

    for phone in phones:
        phone = normalize_whitespace(phone)
        digits = re.sub(r"\D", "", phone)

        if 9 <= len(digits) <= 15:
            cleaned.append(phone)

    return sorted(set(cleaned))


def find_price_text(text: str) -> str:
    lines = re.split(
        r"[.;\n|]+",
        text,
    )

    price_lines = []

    indicators = [
        "€",
        "eur",
        "euro",
        "per day",
        "/day",
        "day",
        "from ",
        "starting",
        "price",
    ]

    for line in lines:
        line = normalize_whitespace(line)

        if not line:
            continue

        lowered = line.lower()

        if any(
            indicator in lowered
            for indicator in indicators
        ):
            if re.search(r"\d", line):
                price_lines.append(line)

    return clean_text(
        " | ".join(price_lines[:8]),
        1200,
    )


def find_car_models(text: str) -> str:
    pattern = (
        r"\b(?:Toyota|Nissan|Ford|Volkswagen|VW|Fiat|Hyundai|Kia|"
        r"Peugeot|Renault|Citroen|Citroën|Opel|Skoda|Škoda|Seat|"
        r"SEAT|Suzuki|Mazda|BMW|Mercedes|Audi|Jeep|Dacia|Volvo|"
        r"Honda|Mitsubishi|Tesla)\b"
        r"(?:\s+[A-Za-z0-9-]{1,20}){0,3}"
    )

    results = re.findall(
        pattern,
        text,
        flags=re.IGNORECASE,
    )

    cleaned = []

    for result in results:
        result = normalize_whitespace(result)

        if result not in cleaned:
            cleaned.append(result)

    return " | ".join(cleaned[:20])


def determine_confidence(
    name: str,
    city: str,
    phone: str,
    email: str,
    website: str,
    relevant: bool,
) -> str:
    score = 0

    if name:
        score += 2

    if city:
        score += 1

    if phone:
        score += 2

    if email:
        score += 2

    if website:
        score += 1

    if relevant:
        score += 2

    if score >= 8:
        return "high"

    if score >= 5:
        return "medium"

    return "low"


# Check whether a URL is allowed by robots.txt

def allowed_by_robots(
    url: str,
    user_agent: str,
) -> bool:
    parsed = urlparse(url)

    if not parsed.scheme or not parsed.netloc:
        return False

    root = f"{parsed.scheme}://{parsed.netloc}"

    if root in ROBOTS_CACHE:
        parser = ROBOTS_CACHE[root]
    else:
        robots_url = urljoin(
            root,
            "/robots.txt",
        )

        parser = RobotFileParser()
        parser.set_url(robots_url)

        try:
            parser.read()
        except Exception:
            ROBOTS_CACHE[root] = parser
            return True

        ROBOTS_CACHE[root] = parser

    try:
        return parser.can_fetch(
            user_agent,
            url,
        )
    except Exception:
        return True


# HTTP fetcher

class WebFetcher:
    def __init__(
        self,
        min_delay: float = DEFAULT_MIN_DELAY,
        max_delay: float = DEFAULT_MAX_DELAY,
        timeout: int = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
    ):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.timeout = timeout
        self.retries = retries
        self.session = requests.Session()

    def get_headers(self) -> dict:
        return {
            "User-Agent": random.choice(
                USER_AGENTS
            ),
            "Accept": (
                "text/html,application/xhtml+xml,"
                "application/xml;q=0.9,*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.8,el;q=0.7",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def fetch(
        self,
        url: str,
    ) -> tuple[str | None, str]:
        url = safe_url(url)

        if not url:
            return None, ""

        for attempt in range(
            self.retries + 1
        ):
            headers = self.get_headers()
            user_agent = headers["User-Agent"]

            if not allowed_by_robots(
                url,
                user_agent,
            ):
                print(
                    f"[robots] blocked: {url}"
                )
                return None, url

            random_delay(
                self.min_delay,
                self.max_delay,
            )

            try:
                response = self.session.get(
                    url,
                    headers=headers,
                    timeout=self.timeout,
                    allow_redirects=True,
                )

                if response.status_code in {
                    429,
                    500,
                    502,
                    503,
                    504,
                }:
                    print(
                        f"[http] {response.status_code}: "
                        f"{url} "
                        f"(attempt {attempt + 1})"
                    )

                    if attempt < self.retries:
                        time.sleep(
                            2 ** attempt
                        )
                        continue

                    return None, url

                response.raise_for_status()

                content_type = (
                    response.headers.get(
                        "Content-Type",
                        "",
                    ).lower()
                )

                if (
                    "text/html" not in content_type
                    and "application/xhtml" not in content_type
                ):
                    return None, response.url

                return response.text, response.url

            except requests.RequestException as exc:
                print(
                    f"[request-error] "
                    f"{url}: {exc}"
                )

                if attempt < self.retries:
                    time.sleep(
                        2 ** attempt
                    )

        return None, url


# Extract JSON-LD data from a page

def extract_jsonld(
    soup: BeautifulSoup,
) -> list[dict]:
    import json

    results = []

    scripts = soup.find_all(
        "script",
        attrs={
            "type": "application/ld+json"
        },
    )

    for script in scripts:
        raw = (
            script.string
            or script.get_text(
                strip=True
            )
        )

        if not raw:
            continue

        try:
            data = json.loads(raw)

            if isinstance(data, dict):
                results.append(data)

            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        results.append(item)

        except Exception:
            continue

    return results


def extract_business_jsonld(
    records: Iterable[dict],
) -> dict:
    useful_types = {
        "LocalBusiness",
        "AutomotiveBusiness",
        "AutoRental",
        "Organization",
        "TravelAgency",
    }

    result = {}

    for item in records:
        item_type = item.get(
            "@type",
            "",
        )

        types = (
            set(item_type)
            if isinstance(item_type, list)
            else {item_type}
        )

        if not types.intersection(
            useful_types
        ):
            continue

        if not result.get("name"):
            result["name"] = str(
                item.get(
                    "name",
                    "",
                )
            )

        if not result.get("telephone"):
            result["telephone"] = str(
                item.get(
                    "telephone",
                    "",
                )
            )

        if not result.get("email"):
            result["email"] = str(
                item.get(
                    "email",
                    "",
                )
            )

        if not result.get("url"):
            result["url"] = str(
                item.get(
                    "url",
                    "",
                )
            )

        address = item.get(
            "address"
        )

        if isinstance(
            address,
            dict,
        ):
            if not result.get("city"):
                result["city"] = str(
                    address.get(
                        "addressLocality",
                        "",
                    )
                )

            if not result.get("region"):
                result["region"] = str(
                    address.get(
                        "addressRegion",
                        "",
                    )
                )

    return result


# Extract useful information from HTML

def extract_page_data(
    html: str,
    final_url: str,
) -> dict:
    soup = BeautifulSoup(
        html,
        "lxml",
    )

    for tag in soup(
        [
            "script",
            "style",
            "noscript",
            "svg",
        ]
    ):
        tag.decompose()

    page_text = clean_text(
        soup.get_text(
            " ",
            strip=True,
        ),
        15000,
    )

    title = ""

    if soup.title:
        title = normalize_whitespace(
            soup.title.get_text(
                " ",
                strip=True,
            )
        )

    description = ""

    meta_description = soup.find(
        "meta",
        attrs={
            "name": re.compile(
                "^description$",
                re.I,
            )
        },
    )

    if meta_description:
        description = normalize_whitespace(
            meta_description.get(
                "content",
                "",
            )
        )

    jsonld_records = extract_jsonld(
        soup
    )

    business_data = extract_business_jsonld(
        jsonld_records
    )

    emails = extract_emails(
        page_text
    )

    phones = extract_phones(
        page_text
    )

    headings = []

    for heading in soup.find_all(
        [
            "h1",
            "h2",
            "h3",
        ]
    )[:15]:
        value = normalize_whitespace(
            heading.get_text(
                " ",
                strip=True,
            )
        )

        if value:
            headings.append(value)

    internal_links = []

    base_host = urlparse(
        final_url
    ).netloc.lower()

    for link in soup.find_all(
        "a",
        href=True,
    ):
        href = link.get(
            "href",
            "",
        ).strip()

        if not href:
            continue

        if href.startswith(
            (
                "mailto:",
                "tel:",
                "javascript:",
                "#",
            )
        ):
            continue

        absolute = safe_url(
            urljoin(
                final_url,
                href,
            )
        )

        if not absolute:
            continue

        link_host = urlparse(
            absolute
        ).netloc.lower()

        if link_host != base_host:
            continue

        link_text = normalize_whitespace(
            link.get_text(
                " ",
                strip=True,
            )
        ).lower()

        path_text = urlparse(
            absolute
        ).path.lower()

        keywords = [
            "contact",
            "about",
            "fleet",
            "cars",
            "vehicles",
            "rental",
            "rent",
            "faq",
            "location",
            "locations",
        ]

        if any(
            keyword in link_text
            or keyword in path_text
            for keyword in keywords
        ):
            internal_links.append(
                absolute
            )

    internal_links = list(
        dict.fromkeys(
            internal_links
        )
    )[:10]

    return {
        "url": final_url,
        "title": title,
        "description": description,
        "text": page_text,
        "jsonld": business_data,
        "emails": emails,
        "phones": phones,
        "headings": " | ".join(
            headings
        ),
        "internal_links": internal_links,
    }


# Generate search queries for nationwide discovery

def generate_queries() -> list[str]:
    queries = list(
        GENERIC_QUERIES
    )

    for location in GREECE_LOCATIONS:
        queries.extend([
            f'"car rental" "{location}" Greece',
            f'"rent a car" "{location}" Greece',
            f'"car hire" "{location}" Greece',
            f'"ενοικίαση αυτοκινήτων" "{location}"',
            f'"rental cars" "{location}" Greece',
        ])

    queries = list(
        dict.fromkeys(
            queries
        )
    )

    random.shuffle(
        queries
    )

    return queries


# Search for rental businesses

def discover_urls(
    queries: Iterable[str],
    max_results_per_query: int,
    max_queries: int,
) -> list[dict]:
    discoveries = []

    queries = list(
        queries
    )[:max_queries]

    ddgs = DDGS(
        timeout=15
    )

    for index, query in enumerate(
        queries,
        start=1,
    ):
        print(
            f"\n[search {index}/{len(queries)}] "
            f"{query}"
        )

        try:
            results = ddgs.text(
                query=query,
                region="gr-el",
                safesearch="moderate",
                max_results=max_results_per_query,
                backend="auto",
            )

            if not results:
                print(
                    "  No results."
                )
                continue

            for result in results:
                href = (
                    result.get("href")
                    or result.get("url")
                    or ""
                )

                if not href:
                    continue

                href = safe_url(
                    href
                )

                if not href:
                    continue

                discoveries.append({
                    "url": href,
                    "title": normalize_whitespace(
                        result.get(
                            "title",
                            "",
                        )
                    ),
                    "snippet": normalize_whitespace(
                        result.get(
                            "body",
                            "",
                        )
                    ),
                    "query": query,
                })

        except Exception as exc:
            print(
                f"[search-error] "
                f"{query}: {exc}"
            )

        random_delay(
            DEFAULT_MIN_DELAY,
            DEFAULT_MAX_DELAY,
        )

    return discoveries


# Remove duplicate URLs from search results

def dedupe_discoveries(
    discoveries: Iterable[dict],
) -> list[dict]:
    unique = {}

    for item in discoveries:
        url = safe_url(
            item.get(
                "url",
                "",
            )
        )

        if not url:
            continue

        if url.lower() not in unique:
            unique[url.lower()] = item

    return list(
        unique.values()
    )


# Convert extracted page data into a rental record

def build_record(
    page_data: dict,
    discovery: dict,
) -> RentalRecord:
    jsonld = page_data.get(
        "jsonld",
        {}
    )

    page_text = page_data.get(
        "text",
        ""
    )

    combined_text = (
        page_text
        + " "
        + page_data.get(
            "description",
            "",
        )
        + " "
        + discovery.get(
            "title",
            "",
        )
        + " "
        + discovery.get(
            "snippet",
            "",
        )
    )

    relevant = looks_like_rental_page(
        combined_text
    )

    name = (
        jsonld.get("name")
        or page_data.get("title")
        or discovery.get("title")
        or ""
    )

    name = re.split(
        r"\s+\|\s+|\s+[-–—]\s+",
        name,
        maxsplit=1,
    )[0]

    name = normalize_whitespace(
        name
    )

    city = normalize_whitespace(
        str(
            jsonld.get(
                "city",
                "",
            )
        )
    )

    region = normalize_whitespace(
        str(
            jsonld.get(
                "region",
                "",
            )
        )
    )

    emails = page_data.get(
        "emails",
        []
    )

    phones = page_data.get(
        "phones",
        []
    )

    email = (
        jsonld.get("email")
        or (
            emails[0]
            if emails
            else ""
        )
    )

    phone = (
        jsonld.get("telephone")
        or (
            phones[0]
            if phones
            else ""
        )
    )

    website = (
        jsonld.get("url")
        or page_data.get(
            "url",
            "",
        )
    )

    business_type = (
        "car_rental_business"
        if relevant
        else "rental_related"
    )

    confidence = determine_confidence(
        name=name,
        city=city,
        phone=phone,
        email=email,
        website=website,
        relevant=relevant,
    )

    return RentalRecord(
        business_name=name,
        business_type=business_type,
        city=city,
        region=region,
        country="Greece",
        website=website,
        source_url=page_data.get(
            "url",
            "",
        ),
        phone=phone,
        email=email,
        car_models=find_car_models(
            combined_text
        ),
        price_text=find_price_text(
            combined_text
        ),
        description=clean_text(
            page_data.get(
                "description",
                "",
            ),
            1000,
        ),
        discovered_from_query=discovery.get(
            "query",
            "",
        ),
        search_result_title=discovery.get(
            "title",
            "",
        ),
        scraped_at=datetime.now(
            timezone.utc
        ).isoformat(),
        confidence=confidence,
    )


# Crawl a discovered website

def crawl_candidate(
    discovery: dict,
    fetcher: WebFetcher,
    max_pages_per_domain: int,
) -> list[RentalRecord]:
    start_url = safe_url(
        discovery.get(
            "url",
            "",
        )
    )

    if not start_url:
        return []

    domain = base_domain(
        start_url
    )

    if not domain:
        return []

    queue = deque([
        start_url
    ])

    visited = set()
    records = []

    while (
        queue
        and len(visited) < max_pages_per_domain
    ):
        current_url = safe_url(
            queue.popleft()
        )

        if not current_url:
            continue

        if current_url in visited:
            continue

        if base_domain(
            current_url
        ) != domain:
            continue

        visited.add(
            current_url
        )

        print(
            f"  [crawl] {current_url}"
        )

        html, final_url = fetcher.fetch(
            current_url
        )

        if not html:
            continue

        try:
            page_data = extract_page_data(
                html,
                final_url,
            )
        except Exception as exc:
            print(
                f"  [parse-error] "
                f"{final_url}: {exc}"
            )
            continue

        combined_text = (
            page_data.get(
                "text",
                "",
            )
            + " "
            + page_data.get(
                "title",
                "",
            )
            + " "
            + discovery.get(
                "snippet",
                "",
            )
        )

        if looks_like_rental_page(
            combined_text
        ):
            record = build_record(
                page_data,
                discovery,
            )

            records.append(
                record
            )

            print(
                f"  [found] "
                f"{record.business_name} | "
                f"{record.phone} | "
                f"{record.email}"
            )

        for link in page_data.get(
            "internal_links",
            [],
        ):
            link = safe_url(
                link
            )

            if not link:
                continue

            if link in visited:
                continue

            if base_domain(
                link
            ) != domain:
                continue

            queue.append(
                link
            )

    return records


# Create a unique identifier for each business

def record_key(
    record: RentalRecord,
) -> str:
    website_domain = base_domain(
        record.website
        or record.source_url
    )

    phone_digits = re.sub(
        r"\D",
        "",
        record.phone
    )

    email = record.email.lower().strip()
    name = record.business_name.lower().strip()
    city = record.city.lower().strip()

    if email:
        return f"email:{email}"

    if phone_digits:
        return f"phone:{phone_digits}"

    if website_domain:
        return f"domain:{website_domain}"

    return f"name:{name}|city:{city}"


# Remove duplicate business records

def dedupe_records(
    records: Iterable[RentalRecord],
) -> list[RentalRecord]:
    unique = {}

    for record in records:
        key = record_key(
            record
        )

        if key not in unique:
            unique[key] = record
            continue

        existing = unique[key]

        existing_score = sum(
            bool(value)
            for value in asdict(
                existing
            ).values()
        )

        new_score = sum(
            bool(value)
            for value in asdict(
                record
            ).values()
        )

        if new_score > existing_score:
            unique[key] = record

    return list(
        unique.values()
    )


# CSV fields

CSV_FIELDS = [
    "business_name",
    "business_type",
    "city",
    "region",
    "country",
    "website",
    "source_url",
    "phone",
    "email",
    "car_models",
    "price_text",
    "description",
    "discovered_from_query",
    "search_result_title",
    "scraped_at",
    "confidence",
]


# Export rental records to CSV

def write_csv(
    records: Iterable[RentalRecord],
    output_file: str,
) -> None:
    records = list(
        records
    )

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=CSV_FIELDS,
            extrasaction="ignore",
        )

        writer.writeheader()

        for record in records:
            writer.writerow(
                asdict(record)
            )


# Command-line arguments

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Dynamically discover and scrape "
            "car rental businesses across Greece."
        )
    )

    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help="CSV output file",
    )

    parser.add_argument(
        "--max-queries",
        type=int,
        default=DEFAULT_MAX_SEARCH_QUERIES,
        help="Maximum number of search queries",
    )

    parser.add_argument(
        "--results-per-query",
        type=int,
        default=DEFAULT_SEARCH_RESULTS,
        help="Search results per query",
    )

    parser.add_argument(
        "--max-pages-per-domain",
        type=int,
        default=DEFAULT_MAX_PAGES_PER_DOMAIN,
        help="Maximum pages crawled per domain",
    )

    parser.add_argument(
        "--min-delay",
        type=float,
        default=DEFAULT_MIN_DELAY,
        help="Minimum delay between requests",
    )

    parser.add_argument(
        "--max-delay",
        type=float,
        default=DEFAULT_MAX_DELAY,
        help="Maximum delay between requests",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help="HTTP timeout",
    )

    parser.add_argument(
        "--retries",
        type=int,
        default=DEFAULT_RETRIES,
        help="Number of HTTP retries",
    )

    return parser.parse_args()


# Main program

def main() -> int:
    args = parse_args()

    print(
        "Greece Car Rental Discovery Scraper"
    )
    print(
        f"[config] output={args.output}"
    )
    print(
        f"[config] max_queries={args.max_queries}"
    )
    print(
        f"[config] results_per_query="
        f"{args.results_per_query}"
    )
    print(
        f"[config] max_pages_per_domain="
        f"{args.max_pages_per_domain}"
    )

    # Generate search queries
    queries = generate_queries()

    print(
        f"\n[discovery] Generated "
        f"{len(queries)} queries."
    )

    # Discover candidate URLs
    discoveries = discover_urls(
        queries=queries,
        max_results_per_query=args.results_per_query,
        max_queries=args.max_queries,
    )

    print(
        f"\n[discovery] Raw URLs: "
        f"{len(discoveries)}"
    )

    # Remove duplicate URLs
    discoveries = dedupe_discoveries(
        discoveries
    )

    print(
        f"[discovery] Unique URLs: "
        f"{len(discoveries)}"
    )

    # Initialize HTTP fetcher
    fetcher = WebFetcher(
        min_delay=args.min_delay,
        max_delay=args.max_delay,
        timeout=args.timeout,
        retries=args.retries,
    )

    all_records = []

    # Crawl discovered websites
    for index, discovery in enumerate(
        discoveries,
        start=1,
    ):
        print()
        print(
            f"[candidate {index}/{len(discoveries)}]"
        )
        print(
            f"URL: {discovery['url']}"
        )

        records = crawl_candidate(
            discovery=discovery,
            fetcher=fetcher,
            max_pages_per_domain=args.max_pages_per_domain,
        )

        all_records.extend(
            records
        )

    # Deduplicate businesses
    print(
        "\n[dedupe] Deduplicating businesses..."
    )

    all_records = dedupe_records(
        all_records
    )

    # Export results
    write_csv(
        all_records,
        args.output,
    )

    # Display summary
    print(
        "\nScraping complete."
    )
    print(
        f"Unique businesses: "
        f"{len(all_records)}"
    )
    print(
        f"CSV output: "
        f"{args.output}"
    )

    confidence_counts = {}

    for record in all_records:
        confidence_counts[
            record.confidence
        ] = confidence_counts.get(
            record.confidence,
            0,
        ) + 1

    print(
        f"Confidence: "
        f"{confidence_counts}"
    )

    return 0


# Program entry point

if __name__ == "__main__":
    try:
        raise SystemExit(
            main()
        )
    except KeyboardInterrupt:
        print(
            "\n[stop] Interrupted by user."
        )
        raise SystemExit(130)
    except Exception as exc:
        print(
            f"\n[fatal] {exc}",
            file=sys.stderr,
        )
        raise SystemExit(1)
```
