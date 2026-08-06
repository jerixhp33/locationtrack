import os
from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from services.link_service import create_tracking_link, deactivate_link

router = APIRouter()


@router.post("/api/links/create")
async def create_link(
    request:      Request,
    case_id:      str = Form(...),
    label:        str = Form(...),
    created_by:   str = Form(default="investigator"),
    disguise:     str = Form(default="default"),
    redirect_url: str = Form(default="https://www.google.com"),
):
    """Create a new tracking link for a case."""
    link = create_tracking_link(case_id, label, created_by, disguise, redirect_url)
    if not link:
        return JSONResponse({"error": "Failed to create link"}, status_code=500)

    # Dynamic base URL resolution (respecting Vercel / reverse proxy HTTPS headers)
    base_url = os.getenv("BASE_URL")
    if not base_url:
        forwarded_proto = request.headers.get("x-forwarded-proto", "https" if request.url.scheme == "https" else "http")
        host = request.headers.get("host") or request.url.netloc
        base_url = f"{forwarded_proto}://{host}"

    tracking_url = f"{base_url.rstrip('/')}/t/{link['slug']}"

    return {
        "tracking_url": tracking_url,
        "slug":         link["slug"],
        "case_id":      link["case_id"],
        "label":        link["label"],
        "disguise":     link.get("disguise", "default"),
        "redirect_url": link.get("redirect_url", "https://www.google.com"),
        "created_at":   link["created_at"],
    }


@router.post("/api/links/deactivate")
async def deactivate(slug: str = Form(...)):
    """Deactivate a tracking link so it stops collecting data."""
    success = deactivate_link(slug)
    return {"status": "deactivated" if success else "not_found"}
