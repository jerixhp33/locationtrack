from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional
from user_agents import parse as ua_parse

from services.ip_lookup import lookup_ip
from services.link_service import get_link_by_slug
from services.supabase_client import supabase

router = APIRouter()


class TrackPayload(BaseModel):
    slug:                 str
    # Original fields
    gps_lat:              Optional[float] = None
    gps_lng:              Optional[float] = None
    gps_accuracy:         Optional[float] = None
    screen_width:         Optional[int]   = None
    screen_height:        Optional[int]   = None
    language:             Optional[str]   = None
    platform:             Optional[str]   = None
    cookie_enabled:       Optional[bool]  = None
    do_not_track:         Optional[str]   = None
    connection_type:      Optional[str]   = None
    referrer:             Optional[str]   = None
    user_agent:           Optional[str]   = None
    # Advanced fingerprint fields (v2.0)
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
    Looks up IP geolocation, parses UA, saves everything to Supabase.
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

    supabase.table("tracking_logs").insert({
        "link_id":              link["id"],
        "slug":                 payload.slug,

        # IP geolocation
        **geo,

        # GPS (browser Geolocation API)
        "gps_lat":              payload.gps_lat,
        "gps_lng":              payload.gps_lng,
        "gps_accuracy":         payload.gps_accuracy,

        # Device info
        "user_agent":           ua_string,
        "browser":              ua.browser.family,
        "browser_version":      ua.browser.version_string,
        "os":                   ua.os.family,
        "os_version":           ua.os.version_string,
        "device_type":          device_type,
        "device_brand":         ua.device.brand,
        "device_model":         ua.device.model,
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

        # Advanced fingerprints (v2.0)
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
    }).execute()

    return {"status": "ok"}
