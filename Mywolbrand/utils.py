# Mywolbrand/utils.py
from user_agents import parse


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip

def parse_user_agent(user_agent_string):
    """Parse user agent string into browser, OS, device type."""
    user_agent = parse(user_agent_string)
    browser = f"{user_agent.browser.family} {user_agent.browser.version_string}"
    os = f"{user_agent.os.family} {user_agent.os.version_string}"
    device_type = user_agent.device.family
    return browser, os, device_type


