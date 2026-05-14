import pytest
import math
from app.services.feature_extractor import extract_features, _is_ip, _get_entropy

def test_is_ip_valid():
    assert _is_ip("192.168.1.1") == 1
    assert _is_ip("8.8.8.8") == 1
    assert _is_ip("2001:0db8:85a3:0000:0000:8a2e:0370:7334") == 1

def test_is_ip_invalid():
    assert _is_ip("google.com") == 0
    assert _is_ip("localhost") == 0
    assert _is_ip("256.256.256.256") == 0
    assert _is_ip("") == 0

def test_get_entropy():
    # Entropy of an empty string is 0
    assert _get_entropy("") == 0.0
    
    # Entropy of a string with all same characters is 0
    assert _get_entropy("aaaa") == 0.0
    
    # Entropy of a string with all unique characters is log2(len)
    unique_str = "abcd"
    assert math.isclose(_get_entropy(unique_str), 2.0)

def test_extract_basic_lengths():
    url = "https://example.com/path?query=1"
    features = extract_features(url)
    
    assert features["url_length"] == len(url)
    assert features["hostname_length"] == len("example.com")
    assert features["path_length"] == len("/path")
    assert features["query_length"] == len("query=1")

def test_extract_has_https():
    features_https = extract_features("https://example.com")
    assert features_https["has_https"] == 1
    
    features_http = extract_features("http://example.com")
    assert features_http["has_https"] == 0

def test_extract_has_at_symbol():
    features_at = extract_features("http://user:pass@example.com")
    assert features_at["has_at_symbol"] == 1
    
    features_no_at = extract_features("http://example.com")
    assert features_no_at["has_at_symbol"] == 0

def test_extract_has_double_slash_redirect():
    features_double = extract_features("http://example.com//http://malicious.com")
    assert features_double["has_double_slash_redirect"] == 1
    
    features_normal = extract_features("http://example.com/path")
    assert features_normal["has_double_slash_redirect"] == 0

def test_extract_has_hyphen_in_domain():
    features_hyphen = extract_features("http://my-bank-secure.com")
    assert features_hyphen["has_hyphen_in_domain"] == 1
    
    features_normal = extract_features("http://mybank.com")
    assert features_normal["has_hyphen_in_domain"] == 0

def test_extract_subdomain_count():
    features_two = extract_features("http://login.secure.paypal.com")
    assert features_two["subdomain_count"] == 2 # login, secure, paypal (the code does count(".") - 1) -> login.secure.paypal.com has 3 dots, 3 - 1 = 2
    
    features_zero = extract_features("http://example.com")
    assert features_zero["subdomain_count"] == 0
    
    features_one = extract_features("http://www.example.com")
    assert features_one["subdomain_count"] == 1

def test_extract_digit_count():
    features = extract_features("http://example.com/123/456")
    assert features["digit_count"] == 6

def test_extract_special_char_count():
    # special chars: @?&=%.-_~
    features = extract_features("http://example.com/path?a=1&b=2")
    assert features["special_char_count"] == 5
    # code uses: sum(ch in "@?&=%.-_~" for ch in url)
    # http://example.com/path?a=1&b=2
    # : is not there. // is not there.
    # . (1)
    # ? (1)
    # = (1)
    # & (1)
    # = (1)
    # total 5
    assert features["special_char_count"] == 5

def test_extract_is_shortener():
    features_short = extract_features("http://bit.ly/12345")
    assert features_short["is_shortener"] == 1
    
    features_normal = extract_features("http://example.com")
    assert features_normal["is_shortener"] == 0

def test_extract_uses_ip_as_host():
    features_ip = extract_features("http://192.168.1.1/login")
    assert features_ip["uses_ip_as_host"] == 1
    
    features_domain = extract_features("http://example.com/login")
    assert features_domain["uses_ip_as_host"] == 0

def test_extract_num_directories():
    features = extract_features("http://example.com/dir1/dir2/file.html")
    assert features["num_directories"] == 3 # /dir1, /dir2, /file.html

    features_none = extract_features("http://example.com")
    assert features_none["num_directories"] == 0

def test_extract_num_parameters():
    features_params = extract_features("http://example.com/?param1=a&param2=b")
    assert features_params["num_parameters"] == 2 # 1 & + 1 if query = 2
    
    features_none = extract_features("http://example.com/")
    assert features_none["num_parameters"] == 0

def test_extract_has_suspicious_warning_words():
    features_suspicious = extract_features("http://secure-login-update.example.com/verify-account")
    # "secure", "login", "update", "verify", "account" = 5
    assert features_suspicious["has_suspicious_warning_words"] == 5
    
    features_clean = extract_features("http://example.com/home")
    assert features_clean["has_suspicious_warning_words"] == 0

def test_extract_handles_missing_schema():
    # Feature extractor should prepend http:// if missing
    features = extract_features("example.com/login")
    assert features["hostname_length"] == len("example.com")
    assert features["path_length"] == len("/login")
    assert features["has_https"] == 0
