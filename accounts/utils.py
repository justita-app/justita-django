from random import randint
import requests
import json
from ippanel import Client
from accounts.models import SmsVerificationCode
import re

def check_phonenumber(value):
    pattern = r'^(\+98|0)9\d{9}$'

    if not re.match(pattern, value):
        return False
    return True


def random_digit(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)


def send_verification_code(phone_number) :

    code = random_digit(4)


    sms = Client("B-mILNC5m_lJcyISEqGz-WD53wV7W2FaMsrPIyJHZd8=")

    message_id = sms.send_pattern("vn04t2dk9fjd9ds", "3000505", phone_number, {"code": code})

    if (message_id) :
        sms = SmsVerificationCode(phone_number=phone_number,code=code)
        sms.save()
        return True

    return False