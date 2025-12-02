# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app import templates
from app.models.db import init_db
from app.routes import auth_router, dashboard_router, habits_router, settings_router

app = FastAPI(title="Sacred Valley")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(habits_router)
app.include_router(settings_router)

@app.on_event("startup")
async def startup():
    init_db()

@app.get("/health")
async def health():
    return {"status": "ok"}