from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

config = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates"
)

mail = FastMail(config)


async def send_verification_email(email: str, username: str, code: str):
    message = MessageSchema(
        subject="Your Twitter Clone verification code",
        recipients=[email],
        template_body={
            "username": username,
            "code": code
        },
        subtype=MessageType.html
    )

    await mail.send_message(message, template_name="verification_email.html")
    