"""Token Shop - Handles token purchases with secret codes."""
import hashlib
import random
import string
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator

app = FastAPI()

# In-memory storage for purchases
purchases = {}

# Price: how much money per token
token_price = 2


class BuyRequest(BaseModel):
    """For buying tokens."""
    username: str
    password: str
    money: int


class CodeRequest(BaseModel):
    """For verifying a code."""
    code: str


class PriceUpdate(BaseModel):
    """For updating the token price."""
    price: int  # must be at least 1

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, price):
        """Reject prices below 1"""
        if price < 1:
            raise ValueError("price must be at least 1")
        return price


@app.post("/buy")
def buy_tokens(payload: BuyRequest):
    """Buy tokens with money. Returns a secret code."""
    # int division. 10 money at price of 2 gives 5 tokens
    tokens_to_give = payload.money // token_price

    # generate a random 32 character string, then hash to a secret code
    random_characters = ''.join(
        random.choices(string.ascii_letters + string.digits, k=32)
    )
    secret_code = hashlib.sha256(random_characters.encode()).hexdigest()

    # store the purchases so /verify can look it up
    purchases[secret_code] = {
        "username": payload.username,
        "tokens": tokens_to_give,
        "used": False,  # true when the code has been redeemed
    }

    return {"secret": secret_code}


@app.post("/verify")
def verify_code(payload: CodeRequest):
    """Check if a secret code is valid and return how many tokens it is worth."""
    # look up the secret code in the purchases above
    existing_purchase = purchases.get(payload.code)

    # the code does not exist
    if not existing_purchase:
        raise HTTPException(status_code=404, detail="Invalid code")

    # the code has already been used. prevent so its not used multiple times
    if existing_purchase["used"]:
        raise HTTPException(
            status_code=400, detail="Code already used"
        )

    # mark the code as used so it cant be redeemed again
    existing_purchase["used"] = True

    return {"tokens": existing_purchase["tokens"]}


@app.get("/price")
def get_price():
    """Return the current token price."""
    return {"price": token_price}


@app.post("/price")
def set_price(payload: PriceUpdate):
    """Admin endpoint to update the token price."""
    global token_price  # update the shared variable, not just inside this function
    token_price = payload.price
    return {"price": token_price}
