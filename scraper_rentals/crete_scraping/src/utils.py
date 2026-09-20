
from __future__ import annotations
import re
from urllib.parse import urlparse, urljoin, urldefrag
import tldextract

EMAIL_RE = re.compile(r'(?i)(?<![\w.+-])([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})(?![\w.-])')
PHONE_RE = re.compile(r'(?<!\d)(?:\+30[\s().-]*|0030[\s().-]*|0)?(?:2\d{9}|69\d{8})(?!\d)')
SOCIAL_HOSTS = {
    "facebook.com": "facebook",
    "instagram.com": "instagram",
    "linkedin.com": "linkedin",
    "tiktok.com": "tiktok",
    "youtube.com": "youtube",
}

def normalize_url(url: str | None) -> str:
    if not url:
        return ""
    url = url.strip()
    if not url:
        return ""
    if url.startswith("//"):
        url = "https:" + url
    elif not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    return urldefrag(url)[0] if parsed.netloc else ""

def domain_key(url: str | None) -> str:
    if not url:
        return ""
    try:
        ext = tldextract.extract(url)
        return ".".join(p for p in (ext.domain, ext.suffix) if p)
    except Exception:
        return ""

def same_site(a: str, b: str) -> bool:
    return bool(domain_key(a) and domain_key(a) == domain_key(b))

def extract_emails(text: str) -> set[str]:
    found = {m.strip(" <>[](){}'\\\".,;:").lower() for m in EMAIL_RE.findall(text or "")}
    return {e for e in found if e.split("@")[-1] not in {"example.com", "wixpress.com", "sentry.io"}}

def normalize_phone(raw: str) -> str:
    digits = re.sub(r"\D", "", raw)
    if digits.startswith("0030"):
        digits = "30" + digits[4:]
    if digits.startswith("30") and len(digits) == 12:
        return "+" + digits
    if len(digits) == 10 and (digits.startswith("2") or digits.startswith("69")):
        return "+30" + digits
    return raw.strip()

def extract_phones(text: str) -> set[str]:
    return {normalize_phone(m) for m in PHONE_RE.findall(text or "")}

def absolutize(base: str, href: str) -> str:
    return normalize_url(urljoin(base, href))

def social_kind(url: str) -> str | None:
    host = urlparse(url).netloc.lower().removeprefix("www.")
    for social_host, kind in SOCIAL_HOSTS.items():
        if host == social_host or host.endswith("." + social_host):
            return kind
    return None
