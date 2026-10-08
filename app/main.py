from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # noqa: F401  (registers tables on Base.metadata)
from app.database import Base, engine
from app.exceptions import register_exception_handlers
from app.routers import auth, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="User Authentication API",
    description="User registration, login and user management with hashed passwords.",
    version="1.0.0",
    lifespan=lifespan,
)

register_exception_handlers(app)
app.include_router(auth.router)
app.include_router(users.router)
