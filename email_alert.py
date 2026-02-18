import smtplib
from email.mime.text import MIMEText
import os

def send_alert(count):
    sender = os.getenv("EMAIL_SENDER")
    receiver = os.getenv("EMAIL_RECEIVER")
    password = os.getenv("EMAIL_PASSWORD")

    msg = MIMEText(f"Alert! People detected: {count}")
    msg['Subject'] = "YOLO People Detection Alert"
    msg['From'] = sender
    msg['To'] = receiver

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())