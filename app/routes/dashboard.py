# app/routes/dashboard.py
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import text
from datetime import date, datetime
from app import templates
import json
from decimal import Decimal
from app.core.db import get_db
from app.routes.auth import get_current_user, row_to_dict

router = APIRouter()

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, tab: str = "habits", user=Depends(get_current_user)):
    if not user:
        return RedirectResponse("/login", 303)

    valid = ["habits", "path", "clans", "settings"]
    active_tab = tab if tab in valid else "habits"

    habits_list = []
    today = date.today().isoformat()
    if active_tab == "habits":
        db = next(get_db())
        habits = db.execute(text("""
            SELECT h.*, MAX(hc.completed_at)::date AS last_completion
            FROM habits h
            LEFT JOIN habit_completions hc ON hc.habit_id = h.id
            WHERE h.user_id = :uid
            GROUP BY h.id
            ORDER BY h.frequency, h.name
        """), {"uid": user["id"]}).fetchall()
        habits_list = [dict(h._mapping) for h in habits]

    # Convert datetime objects to strings
    user_clean = dict(user)

    print(user_clean)
    print(json.dumps(user_clean, indent=4, default=safe_serialize))

    if user_clean.get("created_at"):
        user_clean["created_at"] = user_clean["created_at"].isoformat()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user_json": json.dumps(user_clean, default=safe_serialize),
        "habits_json": json.dumps(habits_list, default=safe_serialize),
        "today": today,
        "active_tab": active_tab
    })


def safe_serialize(obj):
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")