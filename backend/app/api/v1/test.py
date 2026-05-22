from fastapi import APIRouter

from app.services.notification_service import NotificationService

router = APIRouter()


@router.get("/test-email")
async def test_email():
    service = NotificationService()

    service.send_email(
        recipients=["shaswanthbaskaran@gmail.com"],
        subject="MES GBrain Test",
        body="Notification engine is working."
    )

    return {"message": "email sent"}
