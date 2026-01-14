from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date
from db import get_db
from scheduler import start_scheduler
from mail import send_remind_email

app = FastAPI()

class UserIn(BaseModel):
    email: str

class CheckinIn(BaseModel):
    email: str
    date: date

class EmailIn(BaseModel):
    email: str
    days: int



@app.on_event("startup")
def on_startup():
    conn = get_db()
    conn.executescript(open("models.sql").read())
    conn.close()
    start_scheduler()

@app.post("/api/user")
def create_user(data: UserIn):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT OR IGNORE INTO users (email) VALUES (?)",
        (data.email,)
    )

    conn.commit()
    conn.close()
    return {"ok": True}

@app.post("/api/checkin")
def checkin(data: CheckinIn):
    conn = get_db()
    cur = conn.cursor()

    user = cur.execute(
        "SELECT * FROM users WHERE email = ?",
        (data.email,)
    ).fetchone()

    if not user:
        return {"error": "user not found"}

    cur.execute(
        "INSERT INTO checkins (user_id, checkin_date) VALUES (?, ?)",
        (user["id"], data.date.isoformat())
    )

    cur.execute(
        "UPDATE users SET last_checkin_date = ? WHERE id = ?",
        (data.date.isoformat(), user["id"])
    )

    conn.commit()
    conn.close()
    return {"ok": True}

@app.post("/api/send-remind-email")
def send_remind_email_api(data: EmailIn):
    status_code, message = send_remind_email(
        to_email=data.email,
        days=data.days
    )
    return {"code": status_code, "message": message}