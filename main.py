from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from routers import track, ingest, links, dashboard, api_stats

app = FastAPI(
    title="CyberTrack",
    description="Authorized Law Enforcement Use Only",
    version="2.0.0",
    docs_url="/docs",
    redoc_url=None,
)

# Static files (tracker.js)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers
app.include_router(track.router)
app.include_router(ingest.router)
app.include_router(links.router)
app.include_router(dashboard.router)
app.include_router(api_stats.router)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/dashboard")


@app.get("/health")
def health():
    return {"status": "ok", "service": "CyberTrack", "version": "2.0.0"}
