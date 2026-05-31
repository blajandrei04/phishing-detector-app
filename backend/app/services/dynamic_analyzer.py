import socket
import ssl
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

def get_registered_domain(hostname: str) -> str:
    """Extracts the registered domain (e.g., domain.com, sub.co.uk -> sub.co.uk)."""
    hostname = hostname.split(":")[0].lower()
    parts = hostname.split(".")
    if len(parts) < 2:
        return hostname
    
    # Handle double TLDs like co.uk, com.br, net.au
    if len(parts) >= 3:
        second_last = parts[-2]
        last = parts[-1]
        if second_last in {"co", "com", "org", "net", "gov", "edu", "ac"} and len(last) == 2:
            return ".".join(parts[-3:])
            
    return ".".join(parts[-2:])

def resolve_dns(hostname: str) -> dict:
    """Checks if the hostname resolves to an IP address."""
    try:
        ip = socket.gethostbyname(hostname)
        return {"resolved": True, "ip": ip, "error": None}
    except Exception as e:
        return {"resolved": False, "ip": None, "error": str(e)}

def check_ssl(hostname: str) -> dict:
    """Performs an SSL handshake on port 443 and validates the certificate."""
    context = ssl.create_default_context()
    # Don't fail handshake if name mismatch during dynamic analysis, but report validity
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    try:
        with socket.create_connection((hostname, 443), timeout=2.0) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert(binary_form=True)
                if not cert:
                    return {"valid": False, "error": "No certificate presented"}
                
                # Fetch detailed cert data
                # To get text fields, we establish a strict context with CERT_REQUIRED
                try:
                    strict_context = ssl.create_default_context()
                    with socket.create_connection((hostname, 443), timeout=2.0) as strict_sock:
                        with strict_context.wrap_socket(strict_sock, server_hostname=hostname) as strict_ssock:
                            peercert = strict_ssock.getpeercert()
                            
                            expiry_str = peercert.get('notAfter')
                            issuer = dict(x[0] for x in peercert.get('issuer', []))
                            common_name = issuer.get('commonName', '')
                            organization = issuer.get('organizationName', '')
                            
                            valid = True
                            is_expired = False
                            days_until_expiry = 0
                            
                            if expiry_str:
                                # Example: 'Aug 21 12:00:00 2026 GMT'
                                expiry_date = datetime.strptime(expiry_str, '%b %d %H:%M:%S %Y %Z')
                                is_expired = datetime.now(timezone.utc) > expiry_date.replace(tzinfo=timezone.utc)
                                days_until_expiry = (expiry_date.replace(tzinfo=timezone.utc) - datetime.now(timezone.utc)).days
                                if is_expired:
                                    valid = False
                                    
                            return {
                                "valid": valid,
                                "is_expired": is_expired,
                                "days_until_expiry": max(0, days_until_expiry),
                                "issuer_common_name": common_name,
                                "issuer_organization": organization,
                                "error": None
                            }
                except ssl.SSLCertVerificationError as ve:
                    # Connection succeeded but verification failed (e.g. self-signed, invalid chain)
                    return {
                        "valid": False,
                        "is_expired": False,
                        "days_until_expiry": 0,
                        "issuer_common_name": "Unknown (Verification Failed)",
                        "issuer_organization": "Unknown",
                        "error": str(ve)
                    }
    except Exception as e:
        return {"valid": False, "is_expired": True, "days_until_expiry": 0, "error": str(e)}

def query_whois_raw(domain: str) -> str:
    """Queries port 43 of WHOIS servers to retrieve raw registration text."""
    try:
        # Step 1: Query IANA to identify the authoritative registry server
        iana_server = "whois.iana.org"
        with socket.create_connection((iana_server, 43), timeout=2.0) as sock:
            sock.sendall(f"{domain}\r\n".encode("utf-8"))
            response = b""
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                response += data
        
        response_text = response.decode("utf-8", errors="ignore")
        
        referral_server = None
        for line in response_text.splitlines():
            if line.strip().lower().startswith("refer:"):
                referral_server = line.split(":", 1)[1].strip()
                break
        
        # Fallbacks based on TLD
        if not referral_server:
            tld = domain.rsplit(".", 1)[-1].lower()
            if tld == "com" or tld == "net":
                referral_server = "whois.verisign-grs.com"
            elif tld == "org":
                referral_server = "whois.pir.org"
            else:
                referral_server = f"whois.nic.{tld}"
        
        # Step 2: Query the referral WHOIS server
        with socket.create_connection((referral_server, 43), timeout=2.0) as sock:
            sock.sendall(f"{domain}\r\n".encode("utf-8"))
            response = b""
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                response += data
                
        return response.decode("utf-8", errors="ignore")
    except Exception:
        return ""

def parse_creation_date(whois_text: str) -> datetime | None:
    """Parses creation date from raw WHOIS text using various common regex patterns."""
    if not whois_text:
        return None
        
    patterns = [
        r"(?:creation date|created|creation time|registered on|registration date|registered|created on)\s*[:\.]\s*([^\r\n]+)",
    ]
    
    date_formats = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
        "%d-%b-%Y",
        "%Y.%m.%d",
        "%d/%m/%Y",
        "%Y-%m-%d %H:%M:%S",
        "%d.%m.%Y %H:%M:%S",
        "%d-%m-%Y"
    ]
    
    for pattern in patterns:
        for match in re.finditer(pattern, whois_text, re.IGNORECASE):
            date_str = match.group(1).strip()
            # Clean up date string from trailing details/timezones
            clean_str = date_str.split()[0].rstrip('Z')
            
            # Remove any trailing timezone offsets or names
            clean_str = re.sub(r'[\+\-]\d{2}:?\d{2}$', '', clean_str)
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(clean_str, fmt)
                except ValueError:
                    continue
    return None

def check_domain_age(hostname: str) -> dict:
    """Fetches and calculates the age of the registered domain."""
    domain = get_registered_domain(hostname)
    # Check if domain is an IP address
    try:
        socket.inet_aton(domain)
        return {"domain_age_days": None, "creation_date": None, "error": "IP address has no WHOIS records"}
    except socket.error:
        pass

    whois_text = query_whois_raw(domain)
    if not whois_text:
        return {"domain_age_days": None, "creation_date": None, "error": "Could not connect to WHOIS servers"}
        
    creation_date = parse_creation_date(whois_text)
    if creation_date:
        age_days = (datetime.now() - creation_date).days
        return {
            "domain_age_days": max(0, age_days),
            "creation_date": creation_date.strftime("%Y-%m-%d"),
            "error": None
        }
        
    return {"domain_age_days": None, "creation_date": None, "error": "Failed to parse creation date"}

def perform_dynamic_checks(url: str) -> dict:
    """Performs all dynamic analysis checks on the URL's hostname."""
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url
        
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
    except Exception:
        hostname = url
        
    if not hostname:
        return {
            "dns": {"resolved": False, "ip": None, "error": "Invalid URL"},
            "ssl": {"valid": False, "is_expired": True, "days_until_expiry": 0, "error": "Invalid URL"},
            "domain_age": {"domain_age_days": None, "creation_date": None, "error": "Invalid URL"}
        }
        
    dns_res = resolve_dns(hostname)
    
    # If DNS doesn't resolve, SSL and WHOIS might fail or are irrelevant
    if not dns_res["resolved"]:
        return {
            "dns": dns_res,
            "ssl": {"valid": False, "is_expired": True, "days_until_expiry": 0, "error": "DNS resolution failed"},
            "domain_age": {"domain_age_days": None, "creation_date": None, "error": "DNS resolution failed"}
        }
        
    ssl_res = check_ssl(hostname)
    age_res = check_domain_age(hostname)
    
    return {
        "dns": dns_res,
        "ssl": ssl_res,
        "domain_age": age_res
    }
