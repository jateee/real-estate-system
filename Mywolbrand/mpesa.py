import requests
from django.conf import settings
from datetime import datetime
import base64

def stk_push(phone, amount):
    # Format phone number
    phone = format_phone_number(phone)
    
    # Convert amount to integer
    amount = int(round(float(amount)))

    # Timestamp
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    # Password
    password_str = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
    password = base64.b64encode(password_str.encode()).decode()

    # Headers
    headers = {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json"
    }

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": "Wolbrand",
        "TransactionDesc": "Property Purchase"
    }

    response = requests.post(f"{settings.MPESA_BASE_URL}/stkpush/v1/processrequest",
                             json=payload, headers=headers)
    response.raise_for_status()  # Raises HTTPError for bad responses
    return response.json()


def format_phone_number(phone):
    phone = str(phone).strip()
    if phone.startswith("0"):
        phone = "254" + phone[1:]
    elif phone.startswith("+"):
        phone = phone[1:]
    elif not phone.startswith("254"):
        phone = "254" + phone
    return phone


def get_access_token():
    """Retrieve OAuth token from Safaricom."""
    from requests.auth import HTTPBasicAuth
    url = f"{settings.MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(
        url,
        auth=HTTPBasicAuth(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET)
    )
    response.raise_for_status()
    return response.json()["access_token"]

