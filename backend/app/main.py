from fastapi import FastAPI
from sqlalchemy import text

from app.database.database import engine
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.reports import router as reports_router


app = FastAPI(
    title="e-Patrol API",
    version="0.1.0",
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(reports_router)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "e-patrol-api",
    }


@app.get("/health/db")
def database_health_check():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        result.scalar()

    return {
        "status": "ok",
        "database": "connected",
    }