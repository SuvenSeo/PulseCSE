import pytest
from django.core import mail
from backend.models import PortfolioNotification
from backend.tests import factory

@pytest.mark.django_db
class TestPortfolioNotification:
    def test_portfolio_notification_creation(self):
        notification = factory.PortfolioNotificationFactory()
        assert notification.id is not None

    def test_portfolio_notification_str_representation(self):
        notification = factory.PortfolioNotificationFactory()
        assert str(notification) == f"Notification {notification.id} for portfolio {notification.portfolio.id}"

    def test_portfolio_notification_email_send(self):
        notification = factory.PortfolioNotificationFactory()
        mail.send_mail(
            "Test Email",
            "This is a test email",
            "from@example.com",
            ["to@example.com"],
            fail_silently=False,
        )
        assert len(mail.outbox) == 1

    def test_portfolio_notification_email_content(self):
        notification = factory.PortfolioNotificationFactory()
        mail.send_mail(
            "Test Email",
            "This is a test email",
            "from@example.com",
            ["to@example.com"],
            fail_silently=False,
        )
        email = mail.outbox[0]
        assert email.subject == "Test Email"
        assert email.body == "This is a test email"

    def test_portfolio_notification_email_send_on_creation(self, settings):
        settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
        notification = factory.PortfolioNotificationFactory()
        assert len(mail.outbox) == 1

    def test_portfolio_notification_email_content_on_creation(self, settings):
        settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
        notification = factory.PortfolioNotificationFactory()
        email = mail.outbox[0]
        assert email.subject == f"Notification for portfolio {notification.portfolio.id}"
        assert email.body == f"Notification {notification.id} created for portfolio {notification.portfolio.id}"

def test_portfolio_notification_query():
    notifications = PortfolioNotification.objects.all()
    assert notifications.count() == 0

def test_portfolio_notification_query_with_data(factory):
    factory.PortfolioNotificationFactory()
    notifications = PortfolioNotification.objects.all()
    assert notifications.count() == 1

def test_portfolio_notification_query_with_multiple_data(factory):
    factory.PortfolioNotificationFactory()
    factory.PortfolioNotificationFactory()
    notifications = PortfolioNotification.objects.all()
    assert notifications.count() == 2

def test_portfolio_notification_get():
    notification = factory.PortfolioNotificationFactory()
    retrieved_notification = PortfolioNotification.objects.get(id=notification.id)
    assert retrieved_notification.id == notification.id

def test_portfolio_notification_get_with_invalid_id():
    with pytest.raises(PortfolioNotification.DoesNotExist):
        PortfolioNotification.objects.get(id=123)

def test_portfolio_notification_filter():
    notification = factory.PortfolioNotificationFactory()
    filtered_notifications = PortfolioNotification.objects.filter(id=notification.id)
    assert filtered_notifications.count() == 1

def test_portfolio_notification_filter_with_invalid_id():
    filtered_notifications = PortfolioNotification.objects.filter(id=123)
    assert filtered_notifications.count() == 0

def test_portfolio_notification_update():
    notification = factory.PortfolioNotificationFactory()
    notification.message = "New message"
    notification.save()
    updated_notification = PortfolioNotification.objects.get(id=notification.id)
    assert updated_notification.message == "New message"

def test_portfolio_notification_delete():
    notification = factory.PortfolioNotificationFactory()
    notification.delete()
    with pytest.raises(PortfolioNotification.DoesNotExist):
        PortfolioNotification.objects.get(id=notification.id)