from urllib.parse import urlparse
import ipaddress
import re


SHORTENERS = {
    "bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd", "buff.ly"
}


def _is_ip(hostname: str) -> int:
    try:
        ipaddress.ip_address(hostname)
        return 1
    except Exception:
        return 0


def extract_features(url: str) -> dict:
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower()
    path = parsed.path or ""
    query = parsed.query or ""

    # Basic lexical features
    url_length = len(url)
    hostname_length = len(hostname)
    path_length = len(path)
    query_length = len(query)

    # Suspicious pattern flags
    has_https = 1 if parsed.scheme == "https" else 0
    has_at_symbol = 1 if "@" in url else 0
    has_double_slash_redirect = 1 if re.search(r"//.+//", url) else 0
    has_hyphen_in_domain = 1 if "-" in hostname else 0
    subdomain_count = max(0, hostname.count(".") - 1)
    digit_count = sum(ch.isdigit() for ch in url)
    special_char_count = sum(ch in "@?&=%.-_~" for ch in url)
    is_shortener = 1 if hostname in SHORTENERS else 0
    uses_ip_as_host = _is_ip(hostname)

    return {
        "url_length": url_length,
        "hostname_length": hostname_length,
        "path_length": path_length,
        "query_length": query_length,
        "has_https": has_https,
        "has_at_symbol": has_at_symbol,
        "has_double_slash_redirect": has_double_slash_redirect,
        "has_hyphen_in_domain": has_hyphen_in_domain,
        "subdomain_count": subdomain_count,
        "digit_count": digit_count,
        "special_char_count": special_char_count,
        "is_shortener": is_shortener,
        "uses_ip_as_host": uses_ip_as_host,
    }