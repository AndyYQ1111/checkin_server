from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date
from db import get_db
from mail import send_remind_email

def check_absent_users():
    conn = get_db()
    cur = conn.cursor()

    today = date.today()

    users = cur.execute("SELECT * FROM users").fetchall()

    for u in users:
        if not u["last_checkin_date"]:
            continue

        last = date.fromisoformat(u["last_checkin_date"])
        diff = (today - last).days

        if diff >= 3:
            if u["last_remind_date"] == today.isoformat():
                continue

            send_remind_email(u["email"], diff)

            cur.execute(
                "UPDATE users SET last_remind_date = ? WHERE id = ?",
                (today.isoformat(), u["id"])
            )

    conn.commit()
    conn.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        check_absent_users,
        trigger="cron",
        hour=10,
        minute=0
    )
    scheduler.start()
