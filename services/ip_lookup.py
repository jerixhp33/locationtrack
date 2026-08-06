import httpx

FIELDS = (
    "status,message,country,countryCode,region,regionName,"
    "city,zip,lat,lon,timezone,isp,org,as,mobile,proxy,hosting,query"
)

SKIP_IPS = {"127.0.0.1", "::1", "testclient", "localhost"}


async def _lookup_ipapi(ip: str) -> dict:
    """Primary: ip-api.com (free, no key, 45 req/min)."""
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
    """Fallback: ipwho.is (free, no key, unlimited)."""
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
    Multi-source IP geolocation with automatic fallback.
    Tries ip-api.com first, falls back to ipwho.is.
    """
    if not ip or ip in SKIP_IPS:
        return {}

    # Try primary
    result = await _lookup_ipapi(ip)
    if result and result.get("ip_lat"):
        return result

    # Fallback
    result = await _lookup_ipwho(ip)
    if result and result.get("ip_lat"):
        return result

    return {}
