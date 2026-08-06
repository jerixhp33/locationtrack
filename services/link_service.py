from nanoid import generate
from services.supabase_client import supabase

ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789"


def generate_slug(size: int = 8) -> str:
    return generate(alphabet=ALPHABET, size=size)


def create_tracking_link(
    case_id: str,
    label: str,
    created_by: str = "investigator",
    disguise: str = "default",
    redirect_url: str = "https://www.google.com",
) -> dict:
    slug = generate_slug()
    result = (
        supabase.table("tracking_links")
        .insert({
            "slug":         slug,
            "case_id":      case_id,
            "label":        label,
            "created_by":   created_by,
            "is_active":    True,
            "disguise":     disguise,
            "redirect_url": redirect_url,
        })
        .execute()
    )
    return result.data[0] if result.data else {}


def get_link_by_slug(slug: str) -> dict:
    result = (
        supabase.table("tracking_links")
        .select("*")
        .eq("slug", slug)
        .eq("is_active", True)
        .single()
        .execute()
    )
    return result.data or {}


def get_all_links() -> list:
    result = (
        supabase.table("tracking_links")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []


def get_logs_for_link(link_id: str) -> list:
    result = (
        supabase.table("tracking_logs")
        .select("*")
        .eq("link_id", link_id)
        .order("clicked_at", desc=True)
        .execute()
    )
    return result.data or []


def get_link_stats(link_id: str) -> dict:
    """Return aggregated statistics for a tracking link."""
    logs = get_logs_for_link(link_id)
    if not logs:
        return {
            "total_clicks": 0,
            "unique_ips": 0,
            "countries": {},
            "devices": {},
            "browsers": {},
            "vpn_count": 0,
            "mobile_count": 0,
        }

    ips = set()
    countries = {}
    devices = {}
    browsers = {}
    vpn_count = 0
    mobile_count = 0

    for log in logs:
        ip = log.get("ip_address")
        if ip:
            ips.add(ip)

        country = log.get("country") or "Unknown"
        countries[country] = countries.get(country, 0) + 1

        device = log.get("device_type") or "unknown"
        devices[device] = devices.get(device, 0) + 1

        browser = log.get("browser") or "Unknown"
        browsers[browser] = browsers.get(browser, 0) + 1

        if log.get("proxy"):
            vpn_count += 1
        if log.get("is_mobile"):
            mobile_count += 1

    return {
        "total_clicks": len(logs),
        "unique_ips": len(ips),
        "countries": countries,
        "devices": devices,
        "browsers": browsers,
        "vpn_count": vpn_count,
        "mobile_count": mobile_count,
    }


def deactivate_link(slug: str) -> bool:
    result = (
        supabase.table("tracking_links")
        .update({"is_active": False})
        .eq("slug", slug)
        .execute()
    )
    return bool(result.data)
