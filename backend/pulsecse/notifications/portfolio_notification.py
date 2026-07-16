# backend/pulsecse/notifications/portfolio_notification.py

"""
This module handles notifications related to portfolio updates.
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from .models import Portfolio

def send_portfolio_notification(portfolio):
    """
    Send a notification when a portfolio is updated.
    
    Args:
        portfolio (Portfolio): The portfolio instance that was updated.
    """
    subject = "Portfolio Update: {}".format(portfolio.title)
    message = render_to_string('emails/portfolio_notification.html', {
        'portfolio': portfolio,
    })
    from_email = settings.EMAIL_HOST_USER
    to_email = portfolio.user.email
    
    send_mail(subject, message, from_email, [to_email], fail_silently=False)

def notify_portfolio_update(portfolio):
    """
    Notify the user when their portfolio is updated.
    
    Args:
        portfolio (Portfolio): The portfolio instance that was updated.
    """
    send_portfolio_notification(portfolio)