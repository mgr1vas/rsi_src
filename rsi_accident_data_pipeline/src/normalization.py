
from __future__ import annotations
import hashlib
import re
import unicodedata

REGION_ALIASES = {
    "Ηράκλειο": [
        "περιφερειακη ενοτητα ηρακλειου",
        "δημος ηρακλειου",
        "ηρακλειο",
    ],
    "Χανιά": [
        "περιφερειακη ενοτητα χανιων",
        "δημος χανιων",
        "χανια",
    ],
    "Ρέθυμνο": [
        "περιφερειακη ενοτητα ρεθυμνης",
        "περιφερειακη ενοτητα ρεθυμνου",
        "δημος ρεθυμνης",
        "ρεθυμνο",
    ],
    "Λασίθι": [
        "περιφερειακη ενοτητα λασιθιου",
        "λασιθι",
        "δημος αγιου νικολαου",
        "δημος ιεραπετρας",
        "δημος σητειας",
    ],
}

REGION_TEXT_TERMS = {
    "Ηράκλειο": ["ηρακλειο", "ηρακλειου"],
    "Χανιά": ["χανια", "χανιων"],
    "Ρέθυμνο": ["ρεθυμνο", "ρεθυμνης", "ρεθυμνου"],
    "Λασίθι": ["λασιθι", "λασιθιου"],
}

# Explicit normal forms for recurring Greek genitives / ambiguous names.
CANDIDATE_CANONICAL = {
    "χαλεπας": "Χαλέπα",
    "χρυσοπηγης": "Χρυσοπηγή",
    "αγιας βαρβαρας": "Αγία Βαρβάρα",
    "αγιου βασιλειου": "Άγιος Βασίλειος",
    "παλαιοκαστρου": "Παλαιόκαστρο",
    "αδελιανου καμπου": "Αδελιανός Κάμπος",
    "καρτερου": "Καρτερός",
    "χersonisou": "Χερσόνησος",
    "χερσονησου": "Χερσόνησος",
    "ακρωτηριου": "Ακρωτήρι",
    "τυμπακιου": "Τυμπάκι",
    "μοιρων": "Μοίρες",
    "παρηγοριας": "Παρηγοριά",
    "αναληψης χερσονησου": "Ανάληψη Χερσονήσου",
}

GENERIC_CANDIDATES = {
    "βοακ",
    "βορειος οδικος αξονας κρητης",
    "εθνικη οδος",
    "επαρχιακη οδος",
    "κρητη",
    "ηρακλειο",
    "χανια",
    "ρεθυμνο",
    "λασιθι",
}

def strip_accents(value: str) -> str:
    value = unicodedata.normalize("NFD", value or "")
    return "".join(ch for ch in value if unicodedata.category(ch) != "Mn")

def norm(value: str) -> str:
    value = strip_accents(value).lower()
    value = value.replace("–", "-").replace("—", "-")
    value = re.sub(r"\s+", " ", value)
    return value.strip()

def canonical_candidate(value: str) -> str:
    n = norm(value).strip(" ,.;:-")
    return CANDIDATE_CANONICAL.get(n, value.strip())

def stable_record_id(url: str) -> str:
    return "nk_" + hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]

def stable_event_id(urls: list[str]) -> str:
    joined = "|".join(sorted(set(urls)))
    return "evt_" + hashlib.sha1(joined.encode("utf-8")).hexdigest()[:16]

def region_in_geocoded_name(region: str, geocoded_name: str) -> bool:
    n = norm(geocoded_name)
    return any(alias in n for alias in REGION_ALIASES.get(region, []))

def explicit_region_from_text(title: str, location: str) -> str:
    n = norm((title or "") + " " + (location or ""))
    matches = []
    for region, terms in REGION_TEXT_TERMS.items():
        if any(term in n for term in terms):
            matches.append(region)

    # Only override the existing region when the article text is unambiguous.
    return matches[0] if len(set(matches)) == 1 else ""

def expected_region(record: dict) -> tuple[str, str]:
    explicit = explicit_region_from_text(
        record.get("title", ""),
        record.get("location", ""),
    )
    if explicit:
        return explicit, "article_text"

    region = record.get("region", "")
    if region in REGION_ALIASES:
        return region, "source_region"

    return "", "unknown"

def candidate_is_generic(value: str) -> bool:
    return norm(value) in GENERIC_CANDIDATES

def token_overlap(candidate: str, geocoded_name: str) -> float:
    a = {
        t for t in re.findall(r"[a-zα-ω0-9]+", norm(candidate))
        if len(t) >= 4
    }
    b = set(re.findall(r"[a-zα-ω0-9]+", norm(geocoded_name)))
    if not a:
        return 0.0
    return len(a & b) / len(a)
