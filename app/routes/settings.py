# app/routes/settings.py
from fastapi import APIRouter, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy import text
from app.routes.auth import get_current_user
from app.core.db import get_db

router = APIRouter()

@router.post("/settings/username")
async def change_username(new_username: str = Form(...), user=Depends(get_current_user), db=Depends(get_db)):
    if not user: return RedirectResponse("/login", 303)
    db.execute(text("UPDATE users SET username = :u WHERE id = :id"), {"u": new_username, "id": user["id"]})
    db.commit()
    return RedirectResponse("/dashboard?tab=settings", 303)

@router.post("/settings/email")
async def change_email(new_email: str = Form(...), user=Depends(get_current_user), db=Depends(get_db)):
    if not user: return RedirectResponse("/login", 303)
    db.execute(text("UPDATE users SET email = :e WHERE id = :id"), {"e": new_email, "id": user["id"]})
    db.commit()
    return RedirectResponse("/dashboard?tab=settings", 303)

@router.post("/settings/privacy")
async def privacy(show_progress: bool = Form(False), clan_visibility: bool = Form(False),
                  user=Depends(get_current_user), db=Depends(get_db)):
    if not user: return RedirectResponse("/login", 303)
    db.execute(text("UPDATE users SET show_progress_public = :sp, profile_visible_to_clan = :cv WHERE id = :id"),
               {"sp": show_progress, "cv": clan_visibility, "id": user["id"]})
    db.commit()
    return RedirectResponse("/dashboard?tab=settings", 303)

@router.post("/delete-account")
async def delete_account(confirm: str = Form(...), user=Depends(get_current_user), db=Depends(get_db)):
    if not user or confirm != "Delete Account":
        return RedirectResponse("/dashboard", 303)
    db.execute(text("DELETE FROM users WHERE id = :id"), {"id": user["id"]})
    db.commit()
    resp = RedirectResponse("/login")
    resp.delete_cookie("access_token")
    return resp