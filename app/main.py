from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import get_settings
from app.database import create_db_and_tables
from app.routers import auth, dashboard, inventory, reports, technicians, timeclock, users, withdrawals


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(technicians.router)
app.include_router(inventory.router)
app.include_router(withdrawals.router)
app.include_router(reports.router)
app.include_router(users.router)
app.include_router(timeclock.router)
