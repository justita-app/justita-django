from django.conf import settings
import json
import requests


ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/"
merchant_id = settings.ZARINPALMERCHANTID

def send_request(amount , description , callback_url):
    data = {
        'merchant_id' : merchant_id ,
        'amount' : int(amount),
        'description' : description ,
        'callback_url' : callback_url,
        "currency": "IRT"
    }

    data = json.dumps(data)
    headers = {'content-type': 'application/json', 'content-length': str(len(data))}

    try:
        response = requests.post(ZP_API_REQUEST, data=data, headers=headers, timeout=10)
        json_response = response.json()
        if json_response['data']:
            url = ZP_API_STARTPAY + str(json_response['data']['authority'])
            return {'status' : True , 'url' : url , 'authority' : str(json_response['data']['authority'])}
        else :
            return { 'status' : False , 'detail' : f"خطایی رخ داد ، کد خطا ({json_response['errors']['code']})"} 
    except :
        return {'status': False , 'detail' : "خطا در اتصال به درگاه پرداخت"}


def verify_paument(amount , authority) :
    data = {
        "merchant_id": merchant_id,
        "amount": int(amount),
        "authority" : authority
    }
    data = json.dumps(data)

    headers = {'content-type': 'application/json', 'content-length': str(len(data)) }
    try:
        response = requests.post(ZP_API_VERIFY, data=data, headers=headers, timeout=10)
        json_response = response.json()

        if json_response['data'] :
            if json_response['data']['code'] == 100 or json_response['data']['code'] == 101:
                return {'status' : True , 'code' : json_response['data']['code'] , 'ref_id' : json_response['data']['ref_id'] }
            else:
                return {'status': False, 'detail' : f"خطایی رخ داد ، کد خطا ({json_response['data']['code']})"}
        else:
            return { 'status' : False , 'detail' : f"خطایی رخ داد ، کد خطا ({json_response['errors']['code']})"}
    except :
        return {'status': False,'detail' : "خطا در اتصال به درگاه پرداخت"}