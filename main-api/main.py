"""Olympic Games API - Main application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine, Base
from app.routers import users, tokens, countries, athletes, sports, events
from app.seed import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables and seed the database on startup."""
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(users.router, prefix="/v2")
app.include_router(tokens.router, prefix="/v2")
app.include_router(countries.router, prefix="/v2")
app.include_router(athletes.router, prefix="/v2")
app.include_router(sports.router, prefix="/v2")
app.include_router(events.router, prefix="/v2")


@app.get("/")
def root():
    return {"message": "Welcome to the Olympic Games API"}
