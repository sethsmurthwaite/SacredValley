# app/routes/user.py  (create this file)

from fastapi import APIRouter, Depends
from app.routes.auth import get_current_user
from app.core.db import get_db
from sqlalchemy import text

router = APIRouter()

@router.get("/api/user/progress")
async def get_progress(user=Depends(get_current_user), db=Depends(get_db)):
    if not user:
        return {"error": "Not logged in"}

    query = text("""
        WITH ordered_realms AS (
            SELECT 
                name,
                progress_required,
                order_num,
                LEAD(name) OVER (ORDER BY order_num) AS next_realm_name,
                LEAD(progress_required) OVER (ORDER BY order_num) AS next_progress_required
            FROM realms
            ORDER BY order_num
        ),
        user_progress AS (
            SELECT total_progress FROM users WHERE id = :uid
        )
        SELECT 
            u.total_progress,
            -- Current realm: highest realm where progress_required <= user's total
            COALESCE(
                (SELECT name FROM ordered_realms 
                 WHERE progress_required <= (SELECT total_progress FROM user_progress)
                 ORDER BY order_num DESC LIMIT 1),
                'Foundation'
            ) AS current_realm,
            -- Next realm: the one after current
            COALESCE(
                (SELECT next_realm_name FROM ordered_realms 
                 WHERE name = 
                   (SELECT name FROM ordered_realms 
                    WHERE progress_required <= (SELECT total_progress FROM user_progress)
                    ORDER BY order_num DESC LIMIT 1)
                 LIMIT 1),
                'Monarch'
            ) AS next_realm,
            -- Current threshold
            COALESCE(
                (SELECT progress_required FROM ordered_realms 
                 WHERE progress_required <= (SELECT total_progress FROM user_progress)
                 ORDER BY order_num DESC LIMIT 1),
                0
            ) AS current_threshold,
            -- Next threshold
            COALESCE(
                (SELECT next_progress_required FROM ordered_realms 
                 WHERE name = 
                   (SELECT name FROM ordered_realms 
                    WHERE progress_required <= (SELECT total_progress FROM user_progress)
                    ORDER BY order_num DESC LIMIT 1)
                 LIMIT 1),
                (SELECT total_progress FROM user_progress) + 1
            ) AS next_threshold
        FROM users u, user_progress
        WHERE u.id = :uid
    """)

    result = db.execute(query, {"uid": user["id"]}).fetchone()

    total = int(result.total_progress or 0)
    current_threshold = int(result.current_threshold or 0)
    next_threshold = int(result.next_threshold)

    progress_in_level = total - current_threshold
    needed_for_next = next_threshold - total

    return {
        "total_progress": total,
        "current_realm": result.current_realm,
        "next_realm": result.next_realm,
        "progress_in_level": progress_in_level,
        "needed_for_next": needed_for_next,
        "percent_to_next": round((progress_in_level / (next_threshold - current_threshold)) * 100, 2)
        if next_threshold > current_threshold else 100
    }