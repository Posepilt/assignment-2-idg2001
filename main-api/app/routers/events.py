"""Event creation endpoint."""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.olympic_event import OlympicEvent
from app.schemas import OlympicEventCreate
from app.utils.token_dep import consume_token, deduct_token
from app.utils.logger import log_request

router = APIRouter()


@router.post("/event", status_code=201)
def create_event(
    payload: OlympicEventCreate,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(consume_token),
):
    """Add a new event/participation record to the database."""
    new_event = OlympicEvent(
        name=payload.name,
        sex=payload.sex,
        age=payload.age,
        height=payload.height,
        weight=payload.weight,
        team=payload.team,
        noc=payload.noc.upper(),
        games=payload.games,
        year=payload.year,
        season=payload.season,
        city=payload.city,
        sport=payload.sport,
        event=payload.event,
        medal=payload.medal,
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    deduct_token(user, db)
    log_request(user.email, request.url.path)

    return {"message": "Event created", "id": new_event.id}
