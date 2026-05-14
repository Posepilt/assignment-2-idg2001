"""Token management endpoint."""
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas import TokenRedeem

router = APIRouter()

TOKEN_SHOP_URL = "http://token-shop:8001"


@router.get("/tokens")
def get_token_price():
    """Return the current token price from the Token Shop."""
    price_response = httpx.get(f"{TOKEN_SHOP_URL}/price")
    return price_response.json()


@router.post("/tokens")
def redeem_tokens(
    payload: TokenRedeem, db: Session = Depends(get_db)
):
    """Redeem a secret code from the Token Shop for tokens."""
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    shop_response = httpx.post(
        f"{TOKEN_SHOP_URL}/verify",
        json={"code": payload.code},
    )

    if shop_response.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail="Invalid or already used code",
        )

    tokens_to_add = shop_response.json()["tokens"]
    user.tokens += tokens_to_add
    db.commit()
    db.refresh(user)

    return {
        "user_id": user.id,
        "tokens": user.tokens,
        "message": f"Added {tokens_to_add} tokens. New balance: {user.tokens}",
    }
