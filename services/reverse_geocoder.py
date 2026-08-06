import httpx
from typing import Dict, Any, Optional

async def reverse_geocode_gps(lat: float, lng: float) -> Optional[Dict[str, Any]]:
    """
    Translates exact GPS satellite coordinates (lat, lng) into street address,
    suburb, district, and correct city using OpenStreetMap Nominatim.
    """
    if not lat or not lng:
        return None

    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lng}&zoom=18"
        headers = {"User-Agent": "CyberTrack-Forensics/2.2"}
        
        async with httpx.AsyncClient(timeout=4.0) as client:
            r = await client.get(url, headers=headers)
            if r.status_code != 200:
                return None
            data = r.json()
        
        addr = data.get("address", {})
        if not addr:
            return None

        # Build precise local area / suburb / city
        suburb = addr.get("suburb") or addr.get("neighbourhood") or addr.get("village") or addr.get("town") or ""
        city = addr.get("city") or addr.get("county") or addr.get("state_district") or ""
        state = addr.get("state") or ""
        country = addr.get("country") or ""
        country_code = (addr.get("country_code") or "").upper()
        postcode = addr.get("postcode") or ""

        # Formulate display city/area
        if suburb and city and suburb != city:
            display_city = f"{suburb}, {city}"
        else:
            display_city = suburb or city or state

        return {
            "city": display_city,
            "region": state,
            "country": country,
            "country_code": country_code,
            "zip": postcode,
            "full_address": data.get("display_name")
        }

    except Exception:
        return None
