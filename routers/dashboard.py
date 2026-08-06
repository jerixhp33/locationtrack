import os
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services.link_service import get_all_links, get_logs_for_link

router = APIRouter()
TEMPLATES_DIR = os.path.join(Path(__file__).resolve().parent.parent, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main investigator dashboard — lists all tracking links by case."""
    links = get_all_links()
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"links": links},
    )


@router.get("/dashboard/logs/{link_id}", response_class=HTMLResponse)
async def logs(link_id: str, request: Request):
    """Detailed log view for a single tracking link."""
    logs = get_logs_for_link(link_id)
    return templates.TemplateResponse(
        request=request,
        name="logs.html",
        context={"logs": logs, "link_id": link_id},
    )


@router.get("/dashboard/map/{link_id}", response_class=HTMLResponse)
async def map_view(link_id: str, request: Request):
    """Leaflet.js map showing click locations for a link."""
    logs = get_logs_for_link(link_id)

    # Prefer GPS if available, fall back to IP geolocation
    points = []
    for log in logs:
        lat = log.get("gps_lat") or log.get("ip_lat")
        lng = log.get("gps_lng") or log.get("ip_lng")
        if lat and lng:
            source = "GPS" if log.get("gps_lat") else "IP"
            points.append({
                "lat":      lat,
                "lng":      lng,
                "source":   source,
                "accuracy": log.get("gps_accuracy"),
                "label":  (
                    f"{log.get('device_brand', '')} {log.get('device_model', '')} | "
                    f"{log.get('city', '')} {log.get('country', '')} | "
                    f"{log.get('isp', '')} | "
                    f"{log.get('browser', '')} · {log.get('os', '')} | "
                    f"{source} | "
                    f"{str(log.get('clicked_at', ''))[:19]}"
                ).strip(" |"),
            })

    return templates.TemplateResponse(
        request=request,
        name="map.html",
        context={"points": points, "link_id": link_id},
    )
