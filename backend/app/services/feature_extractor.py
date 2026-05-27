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

# Common/trusted TLDs vs exotic/cheap TLDs frequently used in phishing
COMMON_TLDS = {
    "com", "org", "net", "edu", "gov", "mil", "int",
    "co", "io", "us", "uk", "de", "fr", "ca", "au",
    "eu", "jp", "cn", "in", "br", "ru", "nl", "it", "es"
}

# Brand names commonly impersonated in phishing URLs
BRAND_NAMES = [
    "google", "paypal", "apple", "microsoft", "amazon", "netflix",
    "facebook", "instagram", "twitter", "linkedin", "whatsapp",
    "bank", "chase", "wells", "citibank", "hsbc", "barclays",
    "dropbox", "icloud", "outlook", "yahoo", "ebay", "spotify",
    "steam", "discord", "telegram", "coinbase", "binance"
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

def _get_tld_type(hostname: str) -> int:
    """Returns 0 for common/trusted TLDs, 1 for exotic/suspicious TLDs."""
    parts = hostname.rsplit(".", 1)
    if len(parts) < 2:
        return 1  # No TLD found — suspicious
    tld = parts[-1].lower()
    return 0 if tld in COMMON_TLDS else 1

def _get_vowel_consonant_ratio(hostname: str) -> float:
    """Ratio of vowels to consonants in hostname. DGA domains have unnatural ratios."""
    vowels = sum(1 for c in hostname.lower() if c in "aeiou")
    consonants = sum(1 for c in hostname.lower() if c.isalpha() and c not in "aeiou")
    if consonants == 0:
        return 0.0
    return round(vowels / consonants, 4)

def get_sld(hostname: str) -> str:
    """Extract the Second-Level Domain (SLD) of a hostname, handling common double TLDs (e.g. co.uk)."""
    # Remove port if any
    hostname = hostname.split(":")[0].lower()
    parts = hostname.split(".")
    if len(parts) < 2:
        return hostname
    
    # Check if the hostname has a double-part TLD like .co.uk or .com.br
    if len(parts) >= 3:
        second_last = parts[-2]
        last = parts[-1]
        if second_last in {"co", "com", "org", "net", "gov", "edu", "ac"} and len(last) == 2:
            return parts[-3]
            
    return parts[-2]


def _contains_brand_name(url_lower: str, hostname: str) -> int:
    """
    Checks if a known brand name is used as bait.
    A brand name is bait if it appears in the URL but is NOT the main registered domain (SLD).
    """
    sld = get_sld(hostname)
    for brand in BRAND_NAMES:
        if brand in url_lower:
            # If the brand matches the SLD, it's the official site (e.g. google.com)
            if sld == brand:
                continue
            return 1
    return 0

def _has_punycode(url: str) -> int:
    """Detect IDN homograph attacks via punycode (xn-- prefix)."""
    return 1 if "xn--" in url.lower() else 0


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
    
    # Check for suspicious words anywhere in the URL
    has_suspicious_words = sum(1 for word in SUSPICIOUS_WORDS if word in url.lower())

    # ── New features (v2) ──
    tld_type = _get_tld_type(hostname)
    vowel_consonant_ratio = _get_vowel_consonant_ratio(hostname)
    contains_brand_name = _contains_brand_name(url.lower(), hostname)
    punycode_detected = _has_punycode(url)
    path_to_length_ratio = round(path_length / url_length, 4) if url_length > 0 else 0.0

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
        
        # Advanced features:
        "num_directories": num_directories,
        "num_parameters": num_parameters,
        "url_entropy": url_entropy,
        "has_suspicious_warning_words": has_suspicious_words,

        # New v2 features:
        "tld_type": tld_type,
        "vowel_consonant_ratio": vowel_consonant_ratio,
        "contains_brand_name": contains_brand_name,
        "punycode_detected": punycode_detected,
        "path_to_length_ratio": path_to_length_ratio,
    }