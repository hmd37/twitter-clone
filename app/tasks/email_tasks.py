import asyncio

from app.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_verification_email_task(self, email: str, username: str, code: str):
    try:
        from app.utils.email import send_verification_email

        asyncio.run(send_verification_email(email, username, code))
    except Exception as exc:
        raise self.retry(exc=exc)
