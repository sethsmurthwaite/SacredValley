# app/routes/auth.py
from fastapi import APIRouter, Request, Form, Depends, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import text
from app import templates
from app.core.db import get_db
from app.models.user import get_password_hash, verify_password, create_access_token, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError

router = APIRouter()

def row_to_dict(row):
    return dict(row._mapping) if row else None

def get_current_user(access_token: str | None = Cookie(None)) -> dict | None:
    if not access_token:
        return None
    token = str(access_token).strip()
    if token.startswith("Bearer "):
        token = token[7:].strip()
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            return None
    except JWTError:
        return None

    db = next(get_db())
    result = db.execute(text("SELECT * FROM users WHERE username = :u"), {"u": username})
    user = result.fetchone()
    return row_to_dict(user)

@router.get("/", response_class=HTMLResponse)
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db = Depends(get_db)
):
    result = db.execute(text("SELECT * FROM users WHERE username = :u"), {"u": username})
    user = result.fetchone()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    token = create_access_token({"sub": user.username})
    response = RedirectResponse("/dashboard", 303)
    response.set_cookie("access_token", f"Bearer {token}", httponly=True, max_age=604800, path="/", samesite="Lax")
    return response

@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@router.post("/signup")
async def signup(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db = Depends(get_db)
):
    if db.execute(text("SELECT 1 FROM users WHERE username = :u OR email = :e"), {"u": username, "e": email}).fetchone():
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Username or email taken"})
    db.execute(text("INSERT INTO users (username, email, password_hash) VALUES (:u, :e, :p)"),
               {"u": username, "e": email, "p": get_password_hash(password)})
    db.commit()
    token = create_access_token({"sub": username})
    response = RedirectResponse("/dashboard", 303)
    response.set_cookie("access_token", f"Bearer {token}", httponly=True, max_age=604800, path="/", samesite="Lax")
    return response

@router.get("/logout")
async def logout():
    resp = RedirectResponse("/login")
    resp.delete_cookie("access_token", path="/")
    return resp