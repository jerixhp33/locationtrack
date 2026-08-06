import os
import httpx

FIELDS = (
    "status,message,country,countryCode,region,regionName,"
    "city,zip,lat,lon,timezone,isp,org,as,mobile,proxy,hosting,query"
)

SKIP_IPS = {"127.0.0.1", "::1", "testclient", "localhost"}

ABSTRACT_API_KEY = os.getenv("ABSTRACT_API_KEY", "2f5710e8542249a8b6a571ddb09fbee7")
IPINFO_TOKEN = os.getenv("IPINFO_TOKEN", "b62b5ede29146c")


async def _lookup_ipinfo(ip: str) -> dict:
    """IPinfo.io lookup using your token."""
    if not IPINFO_TOKEN:
        return {}
    try:
        url = f"https://ipinfo.io/{ip}/json?token={IPINFO_TOKEN}"
        async with httpx.AsyncClient(timeout=4.0) as client:
            r = await client.get(url)
            data = r.json()
        
        loc_str = data.get("loc", "")
        if not loc_str or "," not in loc_str:
            return {}

        lat_str, lng_str = loc_str.split(",")
        lat = float(lat_str)
        lng = float(lng_str)

        return {
            "ip_address":   data.get("ip"),
            "country":      data.get("country"),
            "country_code": data.get("country"),
            "region":       data.get("region"),
            "city":         data.get("city"),
            "zip":          data.get("postal"),
            "ip_lat":       lat,
            "ip_lng":       lng,
            "timezone":     data.get("timezone"),
            "isp":          data.get("org"),
            "org":          data.get("org"),
            "mobile":       False,
            "proxy":        False,
            "hosting":      False,
        }
    except Exception:
        return {}


async def _lookup_abstractapi(ip: str) -> dict:
    """Abstract IP Intelligence API."""
    if not ABSTRACT_API_KEY:
        return {}
    try:
        url = f"https://ip-intelligence.abstractapi.com/v1/?api_key={ABSTRACT_API_KEY}&ip_address={ip}"
        async with httpx.AsyncClient(timeout=4.0) as client:
            r = await client.get(url)
            data = r.json()
        
        loc = data.get("location") or {}
        comp = data.get("company") or {}
        sec = data.get("security") or {}

        if not loc.get("latitude"):
            return {}

        return {
            "ip_address":   data.get("ip_address"),
            "country":      loc.get("country"),
            "country_code": loc.get("country_code"),
            "region":       loc.get("region"),
            "city":         loc.get("city"),
            "zip":          loc.get("postal_code"),
            "ip_lat":       loc.get("latitude"),
            "ip_lng":       loc.get("longitude"),
            "timezone":     (data.get("timezone") or {}).get("name"),
            "isp":          comp.get("name"),
            "org":          comp.get("name"),
            "mobile":       sec.get("is_mobile", False),
            "proxy":        sec.get("is_proxy", False) or sec.get("is_vpn", False),
            "hosting":      sec.get("is_hosting", False),
        }
    except Exception:
        return {}


async def _lookup_ipapi(ip: str) -> dict:
    """ip-api.com (free, no key, 45 req/min)."""
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            r = await client.get(
                f"http://ip-api.com/json/{ip}",
                params={"fields": FIELDS},
            )
            data = r.json()
        if data.get("status") != "success":
            return {}
        return {
            "ip_address":   data.get("query"),
            "country":      data.get("country"),
            "country_code": data.get("countryCode"),
            "region":       data.get("regionName"),
            "city":         data.get("city"),
            "zip":          data.get("zip"),
            "ip_lat":       data.get("lat"),
            "ip_lng":       data.get("lon"),
            "timezone":     data.get("timezone"),
            "isp":          data.get("isp"),
            "org":          data.get("org"),
            "mobile":       data.get("mobile"),
            "proxy":        data.get("proxy"),
            "hosting":      data.get("hosting"),
        }
    except Exception:
        return {}


async def _lookup_ipwho(ip: str) -> dict:
    """ipwho.is (free, no key, 10,000/mo)."""
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            r = await client.get(f"https://ipwho.is/{ip}")
            data = r.json()
        if not data.get("success", False):
            return {}
        conn = data.get("connection", {})
        return {
            "ip_address":   data.get("ip"),
            "country":      data.get("country"),
            "country_code": data.get("country_code"),
            "region":       data.get("region"),
            "city":         data.get("city"),
            "zip":          data.get("postal"),
            "ip_lat":       data.get("latitude"),
            "ip_lng":       data.get("longitude"),
            "timezone":     (data.get("timezone", {}) or {}).get("id"),
            "isp":          conn.get("isp"),
            "org":          conn.get("org"),
            "mobile":       data.get("type") == "mobile",
            "proxy":        data.get("security", {}).get("proxy", False) if data.get("security") else False,
            "hosting":      data.get("security", {}).get("hosting", False) if data.get("security") else False,
        }
    except Exception:
        return {}


async def lookup_ip(ip: str) -> dict:
    """
    Multi-source IP geolocation with automatic fallback:
    1. IPinfo.io (Token: b62b5ede29146c - High precision city & coordinates)
    2. Abstract IP Intelligence API
    3. ip-api.com
    4. ipwho.is
    """
    if not ip or ip in SKIP_IPS:
        return {}

    # 1. Try IPinfo.io (Your Token)
    result = await _lookup_ipinfo(ip)
    if result and result.get("ip_lat"):
        return result

    # 2. Try Abstract API
    result = await _lookup_abstractapi(ip)
    if result and result.get("ip_lat"):
        return result

    # 3. Fallback to ip-api.com
    result = await _lookup_ipapi(ip)
    if result and result.get("ip_lat"):
        return result

    # 4. Fallback to ipwho.is
    result = await _lookup_ipwho(ip)
    if result and result.get("ip_lat"):
        return result

    return {}
