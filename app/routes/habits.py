# app/routes/habits.py
from fastapi import APIRouter, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy import text
from datetime import date
from app.routes.auth import get_current_user
from app.core.db import get_db

router = APIRouter()

@router.post("/habits")
async def create_habit(
    user=Depends(get_current_user),
    name: str = Form(...),
    description: str = Form(""),
    frequency: str = Form("daily"),
    progress_value: float = Form(10.0),
    repeat_days: int = Form(127),
    db = Depends(get_db)
):
    if not user: return RedirectResponse("/login", 303)
    db.execute(text("""
        INSERT INTO habits (user_id, name, description, frequency, progress_value, repeat_days)
        VALUES (:uid, :n, :d, :f, :pv, :rd)
    """), {"uid": user["id"], "n": name, "d": description, "f": frequency,
           "pv": progress_value, "rd": repeat_days})
    db.commit()
    return RedirectResponse("/dashboard", 303)

@router.post("/habits/{habit_id}/complete")
async def complete_habit(habit_id: int, user=Depends(get_current_user), db=Depends(get_db)):
    if not user: return RedirectResponse("/login", 303)
    today = date.today()
    if db.execute(text("SELECT 1 FROM habit_completions WHERE habit_id = :hid AND completed_at::date = :d"),
                  {"hid": habit_id, "d": today}).fetchone():
        return RedirectResponse("/dashboard", 303)
    db.execute(text("INSERT INTO habit_completions (user_id, habit_id) VALUES (:uid, :hid)"),
               {"uid": user["id"], "hid": habit_id})
    db.commit()
    return RedirectResponse("/dashboard", 303)