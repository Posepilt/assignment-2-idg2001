"""Helper functions for talking to the cache service."""
import httpx


CACHE_URL = "http://cache:8003"  # the address of the cache container inside Docker's network


def get_cached(endpoint: str):
    """Check if the cache has a stored response for this endpoint. Returns None if not found."""
    try:
        cache_response = httpx.get(f"{CACHE_URL}/cache", params={"endpoint": endpoint})
        cache_result = cache_response.json()
        if cache_result["hit"]:
            return cache_result["data"]
    except httpx.ConnectError:
        pass
    return None


def store_cache(endpoint: str, data: dict):
    """Save a response to the cache so the same request can be served faster next time."""
    try:
        httpx.post(f"{CACHE_URL}/cache", json={"endpoint": endpoint, "data": data})
    except httpx.ConnectError:
        pass
