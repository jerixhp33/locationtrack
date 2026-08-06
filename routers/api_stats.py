from fastapi import APIRouter
from services.link_service import get_link_stats

router = APIRouter()


@router.get("/api/stats/{link_id}")
async def get_stats(link_id: str):
    """Return aggregated analytics for a tracking link."""
    stats = get_link_stats(link_id)
    return stats
