import hashlib
import hmac
import json

import requests
import base64

from apps.payment.models import OnlineTransaction


def create_raw_signature(**kwargs):
    rawSignature = "accessKey=" + kwargs.get('accessKey') + "&amount=" + str(kwargs.get(
        'amount')) + "&extraData=" + kwargs.get('extraData') + "&ipnUrl=" + kwargs.get(
        'ipnUrl') + "&orderId=" + str(kwargs.get('orderId')) + "&orderInfo=" + kwargs.get(
        'orderInfo') + "&partnerCode=" + kwargs.get('partnerCode') + "&redirectUrl=" + kwargs.get(
        'redirectUrl') + "&requestId=" + str(kwargs.get('requestId')) + "&requestType=" + kwargs.get('requestType')
    h = hmac.new(bytes(kwargs.get('secretKey'), 'ascii'), bytes(rawSignature, 'ascii'), hashlib.sha256)

    signature = h.hexdigest()
    return signature


def remove_key_from_items(keys, dict):
    for item in keys:
        dict.pop(item)


def create_payment_link(**kwargs):
    endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
    signature = create_raw_signature(**kwargs)
    remove_key_from_items(['accessKey', 'secretKey'], kwargs)
    kwargs['signature'] = signature
    kwargs['lang'] = "en"
    kwargs['autoCapture'] = True
    data = json.dumps(kwargs)
    clen = len(data)
    response = requests.post(endpoint, data=data,
                             headers={'Content-Type': 'application/json', 'Content-Length': str(clen)})
    return signature, response


def create_default(amount, order_id, request_id=None,
                   redirect_url='https://webhook.site/32ccc919-3d1d-4d0d-9c97-deb46bea656e',
                   store_id="Test Store",
                   order_info="pay with momo ",
                   extra_data=""
                   ):
    if not request_id:
        request_id = order_id
    data = {
        'partnerCode': 'MOMOTW0N20220620',
        "accessKey": "Su5rwx2zyD8tXJ8g",
        "secretKey": "mmrwFrTYrImPpDviSAAbVk94VFJRURPX",
        'orderId': str(order_id),
        'storeId': store_id,
        'ipnUrl': "https://262d-103-119-24-120.ngrok.io/api/v1/payment/transacion_event/",
        'amount': str(amount),
        'redirectUrl': redirect_url,
        'orderInfo': order_info,
        'requestId': str(request_id),
        'extraData': extra_data,
        'requestType': "captureWallet"
        # 'orderGroupId': "",
        # 'partnerClientId': 'MOMO',
        # 'partnerName': "MoMo Payment",

    }
    signature, response = create_payment_link(**data)
    return signature, response


def create_momo_payment_link(instance, redirect_url):
    transaction_log = OnlineTransaction.objects.create(company=instance.company, user=instance.investor,
                                                       participant=instance)
    extra_data_raw = {
        'company_id': str(instance.company_id),
        'company_name': str(instance.company.company_name),
        'customer_name': str(instance.company.company_name),
        'customer_id': str(instance.company.user_id),
        'customer_email': str(instance.company.user.email),
    }
    extra_data_bas64 = base64.b64encode(json.dumps(extra_data_raw).encode())
    signature, response = create_default(request_id=instance.pk, order_id=str(transaction_log.id),
                                         redirect_url=redirect_url,
                                         amount=instance.investment_amount,
                                         extra_data=str(extra_data_bas64)
                                         )
    transaction_log.signature = signature
    transaction_log.save()
    response_result = response.json()
    return response_result
