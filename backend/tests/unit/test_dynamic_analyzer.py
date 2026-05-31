import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from app.services.dynamic_analyzer import (
    get_registered_domain,
    resolve_dns,
    parse_creation_date,
    perform_dynamic_checks
)

def test_get_registered_domain():
    assert get_registered_domain("google.com") == "google.com"
    assert get_registered_domain("www.google.com") == "google.com"
    assert get_registered_domain("login.paypal.com") == "paypal.com"
    assert get_registered_domain("sub.domain.co.uk") == "domain.co.uk"
    assert get_registered_domain("bbc.co.uk") == "bbc.co.uk"

@patch("socket.gethostbyname")
def test_resolve_dns_success(mock_gethost):
    mock_gethost.return_value = "1.2.3.4"
    res = resolve_dns("test-domain.com")
    assert res["resolved"] is True
    assert res["ip"] == "1.2.3.4"
    assert res["error"] is None

@patch("socket.gethostbyname")
def test_resolve_dns_failure(mock_gethost):
    mock_gethost.side_effect = Exception("DNS lookup failed")
    res = resolve_dns("invalid-domain.local")
    assert res["resolved"] is False
    assert res["ip"] is None
    assert res["error"] == "DNS lookup failed"

def test_parse_creation_date():
    whois_text = """
    Domain Name: GOOGLE.COM
    Registry Domain ID: 2138514_DOMAIN_COM-VRSN
    Registrar WHOIS Server: whois.markmonitor.com
    Creation Date: 1997-09-15T04:00:00Z
    Updated Date: 2019-09-09T15:39:04Z
    """
    date = parse_creation_date(whois_text)
    assert date is not None
    assert date.year == 1997
    assert date.month == 9
    assert date.day == 15

    # Test alternative pattern
    whois_text_alt = """
    domain:       google.com
    created:      1997-09-15
    changed:      2019-09-09
    """
    date_alt = parse_creation_date(whois_text_alt)
    assert date_alt is not None
    assert date_alt.year == 1997

def test_parse_creation_date_invalid():
    assert parse_creation_date("") is None
    assert parse_creation_date("No creation date matches here") is None

@patch("app.services.dynamic_analyzer.resolve_dns")
@patch("app.services.dynamic_analyzer.check_ssl")
@patch("app.services.dynamic_analyzer.check_domain_age")
def test_perform_dynamic_checks(mock_age, mock_ssl, mock_dns):
    mock_dns.return_value = {"resolved": True, "ip": "1.2.3.4", "error": None}
    mock_ssl.return_value = {"valid": True, "days_until_expiry": 100, "error": None}
    mock_age.return_value = {"domain_age_days": 500, "creation_date": "2020-01-01", "error": None}

    res = perform_dynamic_checks("https://example.com/login")
    assert res["dns"]["resolved"] is True
    assert res["ssl"]["valid"] is True
    assert res["domain_age"]["domain_age_days"] == 500
