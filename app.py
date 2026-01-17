from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date
from db import get_db
from scheduler import start_scheduler, check_absent_users
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
    cur.execute("INSERT OR IGNORE INTO users (email) VALUES (?)", (data.email,))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.post("/api/checkin")
def checkin(data: CheckinIn):
    conn = get_db()
    cur = conn.cursor()
    user = cur.execute("SELECT * FROM users WHERE email = ?", (data.email,)).fetchone()
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
    try:
        send_remind_email(data.email, data.days)
        return {"code": 200, "message": "Email sent successfully."}
    except Exception as e:
        return {"code": 500, "message": f"Failed to send email: {e}"}

@app.post("/api/send-remind-all")
def send_remind_all():
    try:
        check_absent_users()
        return {"code": 200, "message": "Checked all users and sent reminders where needed."}
    except Exception as e:
        return {"code": 500, "message": f"Failed to check users: {e}"}
