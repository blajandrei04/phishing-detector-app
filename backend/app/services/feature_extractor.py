from urllib.parse import urlparse
import ipaddress
import re
import math


SHORTENERS = {
    "bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd", "buff.ly", "cutt.ly", "shorte.st"
}

SUSPICIOUS_WORDS = [
    "login", "update", "verify", "secure", "account", "bank", "confirm", 
    "support", "service", "password", "auth", "credential", "recover"
]

def _is_ip(hostname: str) -> int:
    try:
        ipaddress.ip_address(hostname)
        return 1
    except Exception:
        return 0

def _get_entropy(text: str) -> float:
    if not text:
        return 0.0
    entropy = 0
    for x in set(text):
        p_x = float(text.count(x)) / len(text)
        entropy += - p_x * math.log(p_x, 2)
    return entropy

def extract_features(url: str) -> dict:
    url = str(url).strip()
    if not url.startswith('http://') and not url.startswith('https://'):
        url_for_parsing = 'http://' + url
    else:
        url_for_parsing = url

    try:
        parsed = urlparse(url_for_parsing)
    except ValueError:
        parsed = urlparse(url)
    
    hostname = (parsed.hostname or "").lower()
    path = parsed.path or ""
    query = parsed.query or ""

    # Basic lexical features
    url_length = len(url) # Keep original length
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

    # Advanced Lexical Features
    num_directories = max(0, path.count('/'))
    num_parameters = query.count('&') + (1 if query else 0)
    url_entropy = _get_entropy(url)
    
    # Check for suspicious words anywhere in the URL (excluding query params for simplicity but including path/hostname)
    has_suspicious_words = sum(1 for word in SUSPICIOUS_WORDS if word in url.lower())

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
        
        # New advanced features:
        "num_directories": num_directories,
        "num_parameters": num_parameters,
        "url_entropy": url_entropy,
        "has_suspicious_warning_words": has_suspicious_words
    }