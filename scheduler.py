from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date, timedelta
from db import get_db
from mail import send_remind_email

def check_absent_users():
    conn = get_db()
    cur = conn.cursor()
    today = date.today()

    users = cur.execute("SELECT * FROM users").fetchall()

    for u in users:
        # 使用 last_checkin_date 作为基准
        if u["last_checkin_date"]:
            base_date = date.fromisoformat(u["last_checkin_date"])
        else:
            # 如果从未签到，用注册日作为基准
            # 假设注册日是用户记录的创建日（这里用 id 转换为日期简单模拟）
            # 或者直接假设注册日是今天 - 3 天，保证第三天发送邮件
            base_date = today - timedelta(days=3)

        diff = (today - base_date).days

        # 如果连续未签到 >=3 天，且今天没发过提醒
        if diff >= 3 and u["last_remind_date"] != today.isoformat():
            try:
                send_remind_email(u["email"], diff)
                print(f"Sent reminder to {u['email']} for {diff} days absent.")
            except Exception as e:
                print(f"Failed to send reminder to {u['email']}: {e}")

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
