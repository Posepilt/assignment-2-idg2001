"""Cache service - stores API responses so we don't have to hit the database every time."""
from datetime import datetime, timedelta
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any

app = FastAPI()

cache = {}

# A "hit" means the data was found in the cache
# A "miss" means we did not find it, so we had to query the database
hits = 0
misses = 0


class CacheStore(BaseModel):
    """What the main-api sends us when it wants to store a new response."""
    endpoint: str  # the request url. used as a unique key to look up later
    data: Any  # the response we want to save so we can return it next time the same url is requested


@app.get("/cache")
def get_cache(endpoint: str):
    """Check whether we have a cached response for the given endpoint."""
    global hits, misses

    now = datetime.now()
    cutoff = now - timedelta(minutes=1)  # data older than 1 minute is to old to use

    expired_keys = []
    for key, entry in cache.items():
        if entry["timestamp"] < cutoff:
            expired_keys.append(key)

    # remove expired entries before checking
    for key in expired_keys:
        del cache[key]

    if endpoint in cache:
        hits += 1
        return {"hit": True, "data": cache[endpoint]["data"]}  # cache found. returned saved data

    misses += 1
    return {"hit": False, "data": None}  # cache not found. main-api must ask database


@app.post("/cache")
def set_cache(payload: CacheStore):
    """Store a response so the next identical request can be served from here instead of the database."""
    cache[payload.endpoint] = {
        "data": payload.data,  # the response to save
        "timestamp": datetime.now(),  # when it was saved. used for checking if expired
    }
    return {"message": "Cached"}


@app.get("/log")
def get_log():
    """Return the total number of cache hits and misses since the service started."""
    return {"hits": hits, "misses": misses}
