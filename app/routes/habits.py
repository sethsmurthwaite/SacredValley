# app/routes/habits.py
from fastapi import APIRouter, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy import text
from datetime import date, timedelta
from app.routes.auth import get_current_user
from app.core.db import get_db

router = APIRouter()

@router.post("/habits")
async def create_habit(
    user=Depends(get_current_user),
    name: str = Form(...),
    description: str = Form(""),
    frequency: str = Form("daily"),
    progress_value: int = Form(10),
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
    if not user:
        return RedirectResponse("/login", 303)

    today = date.today()
    uid = user["id"]

    # Prevent double completion today
    already_done = db.execute(text("""
        SELECT 1 FROM habit_completions 
        WHERE habit_id = :hid AND user_id = :uid AND completed_at::date = :today
    """), {"hid": habit_id, "uid": uid, "today": today}).fetchone()

    if already_done:
        return RedirectResponse("/dashboard", 303)

    # Get habit + yesterday's completion for streak logic
    habit = db.execute(text("""
        SELECT h.progress_value, h.streak_current,
               MAX(hc.completed_at::date) FILTER (WHERE hc.completed_at::date < :today) AS yesterday_completed
        FROM habits h
        LEFT JOIN habit_completions hc ON hc.habit_id = h.id AND hc.user_id = :uid
        WHERE h.id = :hid AND h.user_id = :uid
        GROUP BY h.id, h.progress_value, h.streak_current
    """), {"hid": habit_id, "uid": uid, "today": today}).fetchone()

    if not habit:
        return {"error": "Habit not found"}

    gain = int(habit.progress_value or 100)
    current_streak = habit.streak_current or 0
    yesterday_completed = habit.yesterday_completed

    # Determine new streak
    new_streak = current_streak + 1
    if yesterday_completed != today - timedelta(days=1):
        new_streak = 1  # Streak broken!

    # ONE single atomic transaction with proper CTE
    db.execute(text("""
        WITH streak_update AS (
            UPDATE habits 
            SET streak_current = :new_streak,
                streak_max = GREATEST(streak_max, :new_streak)
            WHERE id = :hid AND user_id = :uid
            RETURNING id
        ),
        completion_log AS (
            INSERT INTO habit_completions (user_id, habit_id)
            VALUES (:uid, :hid)
            RETURNING id
        )
        UPDATE users 
        SET total_progress = total_progress + :gain,
            total_habits_completed = total_habits_completed + 1
        WHERE id = :uid
    """), {
        "uid": uid,
        "hid": habit_id,
        "gain": gain,
        "new_streak": new_streak
    })

    db.commit()
    return RedirectResponse("/dashboard", 303)