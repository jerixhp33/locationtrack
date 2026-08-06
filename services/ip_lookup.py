import httpx

FIELDS = (
    "status,message,country,countryCode,region,regionName,"
    "city,zip,lat,lon,timezone,isp,org,as,mobile,proxy,hosting,query"
)

SKIP_IPS = {"127.0.0.1", "::1", "testclient", "localhost"}


async def lookup_ip(ip: str) -> dict:
    """
    Free geolocation via ip-api.com — no API key required.
    Returns location, ISP, mobile/proxy detection.
    """
    if not ip or ip in SKIP_IPS:
        return {}

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
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
