# signals.py
from .utils import get_client_ip, parse_user_agent
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from .models import LoginActivity
import re


def get_client_ip(request):
    """Get client IP from request"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")

def parse_user_agent(user_agent):
    """Simple user agent parser"""
    browser = "Unknown"
    os = "Unknown"
    device = "Unknown"

    if "Windows" in user_agent:
        os = "Windows"
    elif "Mac" in user_agent:
        os = "MacOS"
    elif "Linux" in user_agent:
        os = "Linux"
    elif "Android" in user_agent:
        os = "Android"
    elif "iPhone" in user_agent:
        os = "iOS"

    if "Chrome" in user_agent:
        browser = "Chrome"
    elif "Firefox" in user_agent:
        browser = "Firefox"
    elif "Safari" in user_agent:
        browser = "Safari"
    elif "Edge" in user_agent:
        browser = "Edge"

    if re.search("Mobile|Android|iPhone", user_agent):
        device = "Mobile"
    else:
        device = "Desktop"

    return browser, os, device


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    ip = get_client_ip(request)
    ua = request.META.get("HTTP_USER_AGENT", "unknown")
    browser, os, device = parse_user_agent(ua)

    LoginActivity.objects.create(
        user=user,
        ip_address=ip,
        user_agent=ua,
        browser=browser,
        os=os,
        device_type=device,
        login_success=True
    )


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):

    attempted_user = credentials.get('username') or credentials.get('email') or "unknown"
    
    ip = None
    ua = "unknown"

    if request:  #  request might be None
        ip = get_client_ip(request)
        ua = request.META.get("HTTP_USER_AGENT", "unknown")

    browser, os, device = parse_user_agent(ua)

    LoginActivity.objects.create(
        user=None,  # can't attach to a user because login failed
        attempted_user=attempted_user,
        ip_address=ip or "0.0.0.0",
        user_agent=ua,
        browser=browser,
        os=os,
        device_type=device,
        login_success=False
    )



@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    try:
        last_activity = LoginActivity.objects.filter(user=user, logout_time__isnull=True).latest("login_time")
        last_activity.logout_time = last_activity.login_time  # fallback
        last_activity.save()
    except LoginActivity.DoesNotExist:
        pass

