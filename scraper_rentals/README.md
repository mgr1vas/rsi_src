# Greece Car Rental Discovery Scraper

A standalone Python scraper that dynamically discovers car rental businesses and rental-related websites across Greece using search-engine queries.

The project does not depend on a predefined list of rental company URLs. Instead, it generates location-based and nationwide search queries, discovers candidate websites, visits those websites, extracts relevant business information, removes duplicates, and exports the final dataset as a UTF-8 CSV file.

## Features

* Dynamic discovery of car rental businesses across Greece
* Search-engine-based URL discovery
* Nationwide geographic coverage
* Supports English and Greek rental-related search terms
* Randomized delays between requests
* Rotating User-Agent headers
* HTTP timeout and retry handling
* `robots.txt` checking
* JSON-LD / Schema.org business extraction
* HTML metadata extraction
* Email extraction
* Phone number extraction
* Basic car model detection
* Basic rental price text detection
* Internal-page crawling
* Business deduplication
* Confidence scoring
* UTF-8 CSV export
* Command-line configuration

## How It Works

The scraper follows this pipeline:

```text
Search Query Generation
        ↓
Search Engine Discovery
        ↓
Candidate URLs
        ↓
URL Deduplication
        ↓
robots.txt Check
        ↓
HTTP Fetch
        ↓
HTML / JSON-LD Parsing
        ↓
Business Information Extraction
        ↓
Internal Page Discovery
        ↓
Record Deduplication
        ↓
CSV Export
```

## Requirements

* Python 3.10 or newer
* Internet connection
* A functioning search provider supported by the `ddgs` package

## Installation

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install the required packages:

```powershell
pip install -r requirements.txt
```

## Running the Scraper

Run with the default configuration:

```powershell
python scraper.py
```

By default, the scraper generates:

```text
greece_car_rentals.csv
```

## Custom Output Location

You can specify a different output file:

```powershell
python scraper.py --output output/greece_car_rentals.csv
```

## Configuration Options

### Maximum search queries

```powershell
python greece_car_rental_scraper.py --max-queries 100
```

Controls how many generated search queries are executed.

A larger number can increase discovery coverage but also increases runtime and search-engine requests.

### Search results per query

```powershell
python scraper.py --results-per-query 15
```

Controls how many search results are collected from each query.

### Pages per domain

```powershell
python scraper.py --max-pages-per-domain 6
```

Controls how many pages are crawled for each discovered website.

This allows the scraper to discover pages such as:

```text
/
/about
/contact
/fleet
/cars
/rental
/locations
```

when they are linked from the discovered website.

### Request delays

```powershell
python scraper.py --min-delay 2 --max-delay 5
```

The scraper waits a random amount of time between requests.

This reduces aggressive request patterns and helps prevent unnecessary load on websites.

### HTTP timeout

```powershell
python scraper.py --timeout 20
```

Sets the HTTP request timeout in seconds.

### Retry count

```powershell
python scraper.py --retries 3
```

Controls how many times failed HTTP requests are retried.

## Example Full Run

A more extensive crawl can be started with:

```powershell
python scraper.py `
    --max-queries 100 `
    --results-per-query 15 `
    --max-pages-per-domain 5 `
    --min-delay 2 `
    --max-delay 5 `
    --timeout 20 `
    --retries 3 `
    --output output/greece_car_rentals.csv
```

For PowerShell, the backtick character `` ` `` continues the command onto the next line.

The same command can also be written on one line:

```powershell
python scraper.py --max-queries 100 --results-per-query 15 --max-pages-per-domain 5 --min-delay 2 --max-delay 5 --timeout 20 --retries 3 --output output/greece_car_rentals.csv
```

## Output

The scraper produces a CSV file containing fields such as:

```text
business_name
business_type
city
region
country
website
source_url
phone
email
car_models
price_text
description
discovered_from_query
search_result_title
scraped_at
confidence
```

Example:

```csv
business_name,business_type,city,region,country,website,source_url,phone,email,car_models,price_text,description,discovered_from_query,search_result_title,scraped_at,confidence
Example Rental,car_rental_business,Ioannina,Epirus,Greece,https://example.gr,https://example.gr,+302651000000,info@example.gr,Toyota Yaris | Fiat Panda,€35 per day,Car rental services in Ioannina,...,...,high
```

## Confidence Score

Each record receives a basic confidence level:

```text
high
medium
low
```

The score is based on the amount of information successfully extracted.

For example, a business with:

* a name
* phone number
* email
* website
* location
* rental-related content

will receive a higher confidence score than a page containing only a business name.

## Discovery Strategy

The scraper combines generic nationwide searches with geographic searches.

Examples of generated searches include:

```text
"car rental" Greece
"rent a car" Greece
"car hire" Greece
"ενοικίαση αυτοκινήτων" Ελλάδα
"car rental" Athens Greece
"rent a car" Thessaloniki Greece
"car hire" Rhodes Greece
"ενοικίαση αυτοκινήτων" Ioannina
```

The exact URLs of businesses are not stored in the source code.

This allows the search layer to discover previously unknown businesses dynamically.

## Data Extraction

The scraper attempts to extract information from several sources.

### HTML

The page text, title, headings, metadata, links, telephone numbers, and email addresses are analyzed.

### JSON-LD

Many modern business websites publish Schema.org information in JSON-LD.

The scraper looks for business types such as:

```text
LocalBusiness
AutomotiveBusiness
AutoRental
Organization
TravelAgency
```

This can provide structured information such as:

```text
Business name
Telephone
Email
Website
City
Region
```

## robots.txt

Before fetching a page, the scraper checks the website's `robots.txt` policy.

Pages that are disallowed for the scraper's User-Agent are skipped.

## Rate Limiting

The scraper intentionally introduces randomized delays between HTTP requests and search operations.

Example:

```text
1.5 seconds
2.8 seconds
3.4 seconds
1.9 seconds
```

The exact delay is randomized within the configured range.

## Error Handling

The scraper handles common failures including:

* Connection errors
* Timeout errors
* HTTP errors
* HTTP 429 responses
* Server errors
* Invalid URLs
* Invalid JSON-LD
* Parsing errors
* Search-engine failures

Temporary HTTP failures are retried automatically.

## Deduplication

Businesses can appear in many search results.

The scraper attempts to identify duplicates using:

1. Email address
2. Telephone number
3. Website domain
4. Business name + city

The richest available record is retained.

## Important Limitations

This project is a discovery and data-collection tool, not a guaranteed complete registry of every car rental business in Greece.

Search engines may not index:

* Very small businesses
* Newly created websites
* Businesses with no website
* Websites blocked from indexing
* JavaScript-only content
* Private pages
* Pages requiring authentication

Some websites may also block automated requests.

Therefore, the resulting dataset should be treated as a continuously expandable dataset rather than a definitive list of every rental company in Greece.

## Legal and Ethical Considerations

Only collect publicly accessible information.

The scraper should respect:

* Website terms of service
* `robots.txt`
* Applicable privacy laws
* Applicable data protection regulations
* Search-engine policies
* Reasonable request rates

Do not use the scraper to bypass authentication, access private information, defeat technical access controls, or overload websites.

## Project Structure

Recommended structure:

```text
scraper_rentals/
│
├── scraper.py
├── requirements.txt
├── README.md
│
├── output/
│   └── greece_car_rentals.csv
│
└── .venv/ -> Ignored
```

The `.venv` directory is the local Python virtual environment and should not be committed to Git.

## Git Configuration

If using Git, create a `.gitignore` file:

```gitignore
.venv/
__pycache__/
*.pyc
output/*.csv
.idea/
.vscode/
```

This prevents generated data, Python cache files, and the virtual environment from being committed accidentally.

## Future Improvements

Possible future improvements include:

* PostgreSQL storage
* SQLite storage
* JSON export
* Automatic geographic coordinates
* Province / municipality detection
* Airport pickup detection
* Vehicle category extraction
* Vehicle availability extraction
* Transmission detection
* Fuel-type detection
* Number of seats
* Rental price normalization
* Currency normalization
* Price-per-day extraction
* Website change detection
* Scheduled scraping
* Historical price tracking
* Duplicate business merging
* Notion database integration
* API-based ingestion
* Dashboard visualization
* Automatic data quality scoring

## License

Add the license appropriate for your project before publishing it publicly.

## Author

Marios Grivas - CIO, Lead Developer @ RSI
