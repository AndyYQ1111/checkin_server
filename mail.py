import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_HOST = "smtp.gmail.com"      # Gmail SMTP
SMTP_PORT = 587
SMTP_USER = "qingshye@gmail.com"
SMTP_PASS = "ztixtyqggzzouqic"   # Gmail 应用专用密码

FROM_EMAIL = "qingshye@gmail.com"
FROM_NAME = "活着么"


def send_remind_email(to_email: str, days: int) -> tuple[int, str]:
    """
    发送提醒邮件

    Returns:
        tuple[int, str]: (HTTP-style status code, message)
    """
    try:
        # 构建邮件
        msg = MIMEMultipart()
        msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg["To"] = to_email
        msg["Subject"] = f"你已经连续 {days} 天没有签到啦"

        body = f"""
你好，

你已经连续 {days} 天没有签到，
记得回来签到哦～

—— 记得打卡哦
"""
        msg.attach(MIMEText(body, "plain", "utf-8"))

        # 连接 SMTP
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(FROM_EMAIL, to_email, msg.as_string())
        server.quit()

        return 200, "Email sent successfully"

    except smtplib.SMTPAuthenticationError as e:
        # 登录失败
        return 401, f"SMTP auth failed: {e}"
    except smtplib.SMTPException as e:
        # 其他 SMTP 错误
        return 500, f"SMTP error: {e}"
    except Exception as e:
        # 捕获所有其他异常
        return 500, f"Unexpected error: {e}"
