import json

import requests
from django.conf import settings

from apps.authentication.models import SystemUser


def send_otp_code(phone_number, recapcha_token):
    api_key = settings.FIREBASE_API_KEY
    url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/sendVerificationCode?key={api_key}"
    data = {
        "phoneNumber": phone_number,
        "recaptchaToken": recapcha_token,
    }

    response = requests.post(data=json.dumps(data), headers={"content-type": "application/json"}, url=url)
    return response


def varify_code(session_info, code):
    api_key = settings.FIREBASE_API_KEY
    url = f'https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPhoneNumber?key={api_key}'

    data = {
        "code": code,
        "sessionInfo": session_info
    }
    response = requests.post(data=json.dumps(data), headers={"content-type": "application/json"}, url=url)
    return response


def auth_phone_number_process(phone_number):
    try:
        (phone_number)
        user = SystemUser.objects.get(auth_phone=phone_number)

    except SystemUser.DoesNotExist:
        user = SystemUser.objects.create_user_with_phone(auth_phone=phone_number)
    return user
