import os
import random
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv


load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

if not SENDER_EMAIL or not APP_PASSWORD:
    raise ValueError(
        "SENDER_EMAIL or APP_PASSWORD missing in environment variables"
    )


def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(receiver_email, otp):

    subject = "CSV Analyzer OTP Login"

    body = f"""
Hello,

Your OTP for CSV Analyzer login is:

{otp}

This OTP is valid for a short time.

If you did not request this login, please ignore this email.

Regards,
CSV Analyzer Team
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email.strip()

    server = None

    try:
        server = smtplib.SMTP(
            "smtp.gmail.com",
            587
        )

        server.starttls()
        server.login(
            SENDER_EMAIL,
            APP_PASSWORD
        )

        server.sendmail(
            SENDER_EMAIL,
            receiver_email.strip(),
            msg.as_string()
        )

        return True

    except Exception as e:
        raise Exception(f"OTP send failed: {e}")

    finally:
        if server:
            server.quit()