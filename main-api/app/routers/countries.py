"""Country data endpoint."""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.olympic_event import OlympicEvent
from app.utils.response_format import format_response
from app.utils.token_dep import consume_token, deduct_token
from app.utils.cache import get_cached, store_cache
from app.utils.logger import log_request

router = APIRouter()


@router.get("/country/{noc}")
def get_country(
    noc: str,
    request: Request,
    fmt: str = Query(default="json"),
    db: Session = Depends(get_db),
    user=Depends(consume_token),
):
    """Get all Olympic results for a country, grouped by sport."""
    cache_key = f"{request.url.path}?{request.url.query}"

    cached_data = get_cached(cache_key)
    if cached_data is not None:
        deduct_token(user, db)
        log_request(user.email, cache_key)
        return format_response(cached_data, fmt)

    noc = noc.upper()
    matching_records = db.query(OlympicEvent).filter(OlympicEvent.noc == noc).all()

    if not matching_records:
        raise HTTPException(status_code=404, detail="Country not found")

    deduct_token(user, db)
    log_request(user.email, cache_key)
    sports_summary = {}
    for record in matching_records:
        sport_name = record.sport
        if sport_name not in sports_summary:
            sports_summary[sport_name] = {
                "gold": 0, "silver": 0, "bronze": 0,
                "participations": 0,
            }
        sports_summary[sport_name]["participations"] += 1
        if record.medal == "Gold":
            sports_summary[sport_name]["gold"] += 1
        elif record.medal == "Silver":
            sports_summary[sport_name]["silver"] += 1
        elif record.medal == "Bronze":
            sports_summary[sport_name]["bronze"] += 1

    data = {"noc": noc, "sports": sports_summary}
    store_cache(cache_key, data)

    return format_response(data, fmt)
