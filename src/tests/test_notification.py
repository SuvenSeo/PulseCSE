import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.core.models import AlertType, DeliveryChannel
from src.core.schemas import NotificationRequest
from src.notifications.services import NotificationService

client = TestClient(app)

def test_send_notification():
    notification_request = NotificationRequest(
        alert_type=AlertType.PRICE_ABOVE,
        delivery_channel=DeliveryChannel.EMAIL,
        message="Test notification",
    )
    response = client.post("/api/notifications", json=notification_request.dict())
    assert response.status_code == 200

def test_send_notification_invalid_channel():
    notification_request = NotificationRequest(
        alert_type=AlertType.PRICE_ABOVE,
        delivery_channel="INVALID_CHANNEL",
        message="Test notification",
    )
    response = client.post("/api/notifications", json=notification_request.dict())
    assert response.status_code == 400

def test_notification_service():
    notification_service = NotificationService()
    notification_request = NotificationRequest(
        alert_type=AlertType.PRICE_ABOVE,
        delivery_channel=DeliveryChannel.EMAIL,
        message="Test notification",
    )
    result = notification_service.send_notification(notification_request)
    assert result is True

def test_notification_service_invalid_channel():
    notification_service = NotificationService()
    notification_request = NotificationRequest(
        alert_type=AlertType.PRICE_ABOVE,
        delivery_channel="INVALID_CHANNEL",
        message="Test notification",
    )
    with pytest.raises(ValueError):
        notification_service.send_notification(notification_request)