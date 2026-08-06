import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse

from routers import track, ingest, links, dashboard, api_stats, auth
from services.auth_service import is_authenticated

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = FastAPI(
    title="CyberTrack",
    description="Authorized Law Enforcement Use Only",
    version="2.1.0",
    docs_url="/docs",
    redoc_url=None,
)

# Authentication Guard Middleware
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path

    # Public paths that never require authentication
    public_prefixes = [
        "/login",
        "/logout",
        "/t/",
        "/api/ingest",
        "/health",
        "/static/",
        "/favicon.ico"
    ]

    # Check if path is public
    is_public = path == "/" or any(path.startswith(prefix) for prefix in public_prefixes)

    if not is_public:
        if not is_authenticated(request):
            # If requesting HTML pages, redirect to /login
            if path.startswith("/dashboard") or path.startswith("/docs"):
                return RedirectResponse(url="/login", status_code=302)
            # If requesting backend API endpoints, return 401 Unauthorized
            return JSONResponse(status_code=401, content={"detail": "Authentication required. Access denied."})

    response = await call_next(request)
    return response


# Static files
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Routers
app.include_router(auth.router)
app.include_router(track.router)
app.include_router(ingest.router)
app.include_router(links.router)
app.include_router(dashboard.router)
app.include_router(api_stats.router)


@app.get("/", include_in_schema=False)
def root(request: Request):
    if is_authenticated(request):
        return RedirectResponse(url="/dashboard")
    return RedirectResponse(url="/login")


@app.get("/health")
def health():
    return {"status": "ok", "service": "CyberTrack", "version": "2.1.0"}
