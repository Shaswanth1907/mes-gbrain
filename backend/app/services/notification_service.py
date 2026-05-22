import smtplib
from email.message import EmailMessage

from app.config.env_config import settings


class NotificationService:
    def __init__(self):
        self.smtp_username = settings.smtp_username.strip()
        # Gmail app passwords are often copied with spaces every 4 chars.
        self.smtp_password = settings.smtp_password.replace(" ", "").strip()
        self.smtp_from = settings.smtp_from.strip()
        self.smtp_server = settings.smtp_server.strip()
        self.smtp_port = int(settings.smtp_port)

    def send_email(self, recipients, subject, body):
        self._send_email_sync(
            recipients,
            subject,
            body
        )

    def _send_email_sync(self, recipients, subject, body):
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self.smtp_from
        message["To"] = ", ".join(recipients)
        message.set_content(body)

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(message)
