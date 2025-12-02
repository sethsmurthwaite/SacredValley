# app/main.py
from fastapi import FastAPI, Request, Form, Depends, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker
from jose import jwt, JWTError
from datetime import date

from app.models.user import (
    get_password_hash,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM
)

from app.models.db import init_db

app = FastAPI(title="Sacred Valley")
@app.on_event("startup")
async def startup_event():
    init_db()  # Creates/updates all tables + hypertables
    print("Database schema verified and up to date.")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

DATABASE_URL = "postgresql://sacred:valley123@localhost:5432/sacredvalley"
engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    result = db.execute(
        text("SELECT id, username, email, current_realm, progress_to_next, madra_type FROM users WHERE username = :u"),
        {"u": username}
    )
    return row_to_dict(result.fetchone())

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    user = get_current_user()
    if user:
        return RedirectResponse("/dashboard", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup")
async def signup(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    if db.execute(text("SELECT 1 FROM users WHERE username = :u OR email = :e"), {"u": username, "e": email}).fetchone():
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Username or email already taken"})
    db.execute(text("""
        INSERT INTO users (username, email, password_hash, current_realm, madra_type, progress_to_next)
        VALUES (:u, :e, :p, 'Mortal', 'Pure', 0.0)
    """), {"u": username, "e": email, "p": get_password_hash(password)})
    db.commit()
    token = create_access_token({"sub": username})
    response = RedirectResponse("/dashboard", status_code=303)
    response.set_cookie("access_token", f"Bearer {token}", httponly=True, max_age=604800, path="/", samesite="Lax")
    return response

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    result = db.execute(text("SELECT * FROM users WHERE username = :u"), {"u": username})
    user = result.fetchone()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    token = create_access_token({"sub": user.username})
    response = RedirectResponse("/dashboard", status_code=303)
    response.set_cookie("access_token", f"Bearer {token}", httponly=True, max_age=604800, path="/", samesite="Lax")
    return response

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user=Depends(get_current_user)):
    if not user:
        return RedirectResponse("/login", status_code=303)

    db = next(get_db())

    habits = db.execute(text("""
        SELECT 
            h.id, h.name, h.description, h.frequency, h.progress_value,
            h.streak_current, h.streak_max,
            MAX(hc.completed_at)::date AS last_completion
        FROM habits h
        LEFT JOIN habit_completions hc ON hc.habit_id = h.id
        WHERE h.user_id = :uid
        GROUP BY h.id
        ORDER BY h.frequency, h.name
    """), {"uid": user["id"]}).fetchall()

    today = date.today().isoformat()
    habits_list = [row_to_dict(h) for h in habits]

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "habits": habits_list,
        "today": today
    })

@app.post("/habits")
async def create_habit(
    request: Request,
    user=Depends(get_current_user),
    name: str = Form(...),
    description: str = Form(""),
    frequency: str = Form("daily"),
    progress_value: float = Form(10.0),
    repeat_days: int = Form(127),
    db: Session = Depends(get_db)
):
    if not user:
        return RedirectResponse("/login", status_code=303)
    db.execute(text("""
        INSERT INTO habits (user_id, name, description, frequency, progress_value, repeat_days)
        VALUES (:uid, :n, :d, :f, :pv, :rd)
    """), {"uid": user["id"], "n": name, "d": description, "f": frequency,
           "pv": progress_value, "rd": repeat_days})
    db.commit()
    return RedirectResponse("/dashboard", status_code=303)

@app.post("/habits/{habit_id}/complete")
async def complete_habit(habit_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return RedirectResponse("/login", status_code=303)

    habit = db.execute(text("SELECT id FROM habits WHERE id = :hid AND user_id = :uid"),
                       {"hid": habit_id, "uid": user["id"]}).fetchone()
    if not habit:
        return HTMLResponse("Not found", status_code=404)

    today = date.today()
    already = db.execute(text("""
        SELECT 1 FROM habit_completions
        WHERE habit_id = :hid AND completed_at::date = :today
    """), {"hid": habit_id, "today": today}).fetchone()

    if already:
        return RedirectResponse("/dashboard", status_code=303)

    db.execute(text("INSERT INTO habit_completions (user_id, habit_id) VALUES (:uid, :hid)"),
               {"uid": user["id"], "hid": habit_id})
    db.commit()
    return RedirectResponse("/dashboard", status_code=303)

@app.get("/logout")
async def logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie("access_token", path="/")
    return response

@app.get("/health")
async def health():
    return {"status": "ok"}