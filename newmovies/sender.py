import smtplib
from email.message import EmailMessage

from . import config


def send(subject, html_body, text_body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = config.GMAIL_ADDRESS
    msg["To"] = ", ".join(config.EMAIL_TO)
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(config.GMAIL_ADDRESS, config.GMAIL_APP_PASSWORD)
        server.send_message(msg)
