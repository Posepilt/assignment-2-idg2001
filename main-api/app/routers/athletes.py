"""Athlete data endpoint."""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.olympic_event import OlympicEvent
from app.utils.response_format import format_response
from app.utils.token_dep import consume_token, deduct_token
from app.utils.cache import get_cached, store_cache
from app.utils.logger import log_request

router = APIRouter()


@router.get("/athlete/{name}")
def get_athlete(
    name: str,
    request: Request,
    fmt: str = Query(default="json"),
    db: Session = Depends(get_db),
    user=Depends(consume_token),
):
    """Search for an athlete by name and return their Olympic results."""
    cache_key = f"{request.url.path}?{request.url.query}"

    cached_data = get_cached(cache_key)
    if cached_data is not None:
        deduct_token(user, db)
        log_request(user.email, cache_key)
        return format_response(cached_data, fmt)

    search_name = name.replace("-", " ")
    matching_records = db.query(OlympicEvent).filter(
        OlympicEvent.name.ilike(f"%{search_name}%")
    ).all()

    if not matching_records:
        raise HTTPException(status_code=404, detail="Athlete not found")

    deduct_token(user, db)
    log_request(user.email, cache_key)
    results = []
    for record in matching_records:
        results.append({
            "name": record.name,
            "sport": record.sport,
            "event": record.event,
            "year": record.year,
            "city": record.city,
            "noc": record.noc,
            "medal": record.medal,
        })

    data = {"athlete": name, "count": len(results), "results": results}
    store_cache(cache_key, data)

    return format_response(data, fmt)
