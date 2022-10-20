from binance.pay.merchant import Merchant as Client


# Setup merchant API from https://developers.binance.com/docs/binance-pay/api-order-create-v2


def create_payment_link(trade_num, amount, company_id, company_name, customer_email, customer_id, company_details=None,
                        currency='USDT', terminal_type='WEB'):
    parameters = parameter_builder(amount, company_details, company_id, company_name, currency, customer_email,
                                   customer_id, trade_num, terminal_type=terminal_type)
    api_key, api_secret = get_binance_pay_credential()
    client = Client(key=api_key, secret=api_secret)
    response = client.new_order(parameters)
    return response


def parameter_builder(amount, company_details, company_id, company_name, currency, customer_email, customer_id,
                      trade_num, terminal_type):
    parameters = {
        "env": {
            "terminalType": terminal_type
        },
        "merchantTradeNo": trade_num,
        "orderAmount": amount,
        "currency": currency,
        "goods": {
            "goodsType": "02",
            "goodsCategory": "Z000",
            "referenceGoodsId": company_id,
            "goodsName": company_name,
            "goodsDetail": company_details,
        },
        "buyer": {
            'buyerEmail': customer_email,
            "referenceBuyerId": customer_id,
        },
        "returnUrl": "https://webhook.site/#!/dabd0099-e813-4d3c-bf64-0a338d3fa83e",
        'cancelUrl': "https://webhook.site/#!/dabd0099-e813-4d3c-bf64-0a338d3fa83e",
    }
    return parameters


def get_binance_pay_credential():
    api_key = 'lt59laezmrgcprzqt3c15r5cbeil2umwshc3zcpdku9amuvmmvp4nvv4muvune5b'
    api_secret = '9mx0nqatjdqfavhoga5xf3yrjsyjey0buwhj9tqxwiyipsswvlnio1oxe2sx1qml'
    return api_key, api_secret
