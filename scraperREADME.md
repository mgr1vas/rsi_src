# RoadSafetyInsights — Naxos Data Scraper Documentation

This Python utility automates historical data collection regarding traffic accidents, road hazards, and police reports on the island of Naxos. It targets local news portals and municipal announcement frameworks to establish a base dataset for the **RoadSafetyInsights** MVP.

---

# 1. System Overview & Architecture

The scraper operates as a multi-site configuration matrix. Rather than deploying isolated scripts for individual URLs, the engine reads specific structural rules (HTML tags, CSS target classes, and pagination templates) from a centralized registry (`site_rules`), allowing scaling to additional target portals without modification of core logic.

```text
              ┌──────────────────────────────┐
              │   Central Rule Registry      │
              │ (CSS Selectors & Paths)      │
              └──────────────┬───────────────┘
                             │
                             ▼
┌──────────────┐     ┌──────────────────────────────┐     ┌──────────────────────────────────┐
│ Target Web   │ ──> │ Scraper Core Module          │ ──> │ Double-Filter Evaluator          │
│ News Pages   │     │ (Requests/BeautifulSoup4)    │     │ (Accident + Location Matching)   │
└──────────────┘     └──────────────────────────────┘     └──────────────┬───────────────────┘
                                                                          │
                                                                          ▼
                                                       ┌──────────────────────────────┐
                                                       │ Standardized Dataset Export  │
                                                       │ (naxos_accidents.csv UTF-8)  │
                                                       └──────────────────────────────┘
```

---

# 2. Prerequisites & Setup

The engine relies on standard HTTP networking libraries and an HTML tree-parser framework.

## Dependencies Installation

Run the following command to install the required libraries:

```bash
pip install requests beautifulsoup4
```

## Script Execution

Execute the scraper using Python 3:

```bash
python scrape_naxos.py
```

Ensure your terminal properly supports UTF-8 encoding so that Greek characters are displayed correctly during execution.

---

# 3. Data Flow & Evaluation Framework

## Core Mechanics

### Dynamic Pagination Traversal

The module requests sequentially mapped pages up to a user-defined threshold (`pages_to_scrape = 10`), mimicking natural human browsing behavior across archive pages.

### Politeness Throttling

To prevent IP bans or unnecessary load on local hosting infrastructures, randomized delays between **1.5 and 3.0 seconds** are inserted before each HTTP request.

### Double-Filtering Pipeline

#### Accident Filtering

The scraper evaluates headlines and summaries against normalized Greek word roots such as:

- `τροχαι`
- `ατυχημ`
- `συγκρουσ`

Using clipped root forms allows matching across different grammatical cases, plural forms, capitalization, and inflections.

#### Location Matching

Each candidate article is additionally checked for explicit references to **Naxos**, using the normalized root:

- `ναξ`

Only records satisfying **both** the accident filter and the location filter are exported.

---

## Target Output Schema (`naxos_accidents.csv`)

The final dataset is written using **UTF-8 with BOM (`utf-8-sig`)** to ensure proper rendering inside Microsoft Excel, Google Sheets, and modern database tools.

| Column Header | Data Type | Purpose / Description |
|--------------|----------|-----------------------|
| `source` | String | Origin news portal (e.g. Kykladiki Police, Naxos Press) |
| `title` | String | Cleaned article headline |
| `summary` | String | Short article excerpt describing the incident |
| `link` | String | Absolute URL pointing to the original article |

---

# 4. Engineering Challenges Encountered

Developing a reliable extraction framework for hyper-local regional news outlets required solving several structural and linguistic challenges.

## Theme Inconsistencies & Missing Article Nodes

Many regional websites do not utilize semantic HTML5 `<article>` elements. Initial parsing attempts returned empty datasets because the pages instead relied on deeply nested `<div>` structures.

The scraper was refactored to treat heading elements (`<h2>` / `<h3>`) containing hyperlinks as primary entry points, then traverse surrounding containers to recover article summaries.

---

## Greek Accent Normalization

Greek words frequently contain stress accents (τόνοι), for example:

- τροχαίο
- ΤΡΟΧΑΙΑ
- ατύχημα

Standard case-insensitive matching in Python is insufficient because accented and non-accented Unicode characters differ.

A normalization layer removes all accent marks before keyword evaluation, allowing reliable comparison regardless of capitalization or diacritics.

---

## Regional False Positives

Local police feeds often publish incidents occurring throughout the Cyclades (e.g. Syros, Mykonos, Paros), not exclusively on Naxos.

Simple accident keyword filtering therefore produced numerous irrelevant results.

A second validation stage was introduced requiring the article to explicitly reference **Naxos** before acceptance.

---

## Excel Greek Character Corruption

Writing CSV files using standard UTF-8 resulted in unreadable Greek text when opened directly in Microsoft Excel.

This occurred because Excel frequently assumes legacy encodings.

Saving the dataset using **UTF-8 with BOM (`utf-8-sig`)** forces spreadsheet software to correctly recognize Unicode Greek characters.

---

## Historical Archive Depth

Searching only the landing page frequently returned zero accident reports during quiet periods.

Support for archive pagination using routes such as:

```text
/page/{number}/
```

allowed the scraper to explore historical content and generate a significantly richer initial dataset for the RoadSafetyInsights MVP.
