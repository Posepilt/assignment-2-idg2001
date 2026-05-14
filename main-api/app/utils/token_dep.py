"""Token consumption dependency for data endpoints."""
import time
import httpx
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User

RATE_LIMITER_URL = "http://rate-limiter:8002"


def consume_token(
    x_user_id: str = Header(...),
    db: Session = Depends(get_db),
):
    """Check the user exists, has tokens left, and apply rate limiting."""
    user = db.query(User).filter(User.id == x_user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user ID")
    if user.tokens <= 0:
        raise HTTPException(status_code=403, detail="No tokens remaining")

    try:
        httpx.post(
            f"{RATE_LIMITER_URL}/{x_user_id}",
            json={"username": user.email},
        )
        rate_limiter_response = httpx.get(f"{RATE_LIMITER_URL}/{x_user_id}")
        rate_limiter_data = rate_limiter_response.json()
        if rate_limiter_data["delay"] > 0:
            time.sleep(rate_limiter_data["delay"])
    except httpx.ConnectError:
        pass  # rate limiter might not be running, thats ok

    return user


def deduct_token(user: User, db: Session) -> None:
    """Remove one token from the user's balance."""
    user.tokens -= 1
    db.commit()
