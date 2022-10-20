import uuid

from django.conf import settings
from django.db import models

# class TransactionHistory(models.Model):
#     partner_code = models.TextField(null=True)
#     order_id = models.TextField(null=True)
#     request_id = models.TextField(null=True)
#     amount = models.IntegerField(null=True)
#     order_info = models.TextField(null=True)
#     order_type = models.TextField(null=True)
#     trans_id = models.TextField(null=True)
#     result_code = models.TextField(null=True)
#     message = models.TextField(null=True)
#     pay_type = models.TextField(null=True)
#     response_time = models.TextField(null=True)
#     extra_data = models.JSONField(null=True)
#     signature = models.TextField(null=True)
#
#     class Meta:
#         db_table = 'transaction_history'
from apps.company.models import Company
from apps.investment.models import InvestmentParticipation


class OnlineTransaction(models.Model):
    EMPTY_TRANSACTION = 'empty'
    SUCCESS_TRANSACTION = 'Successful.'
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    company = models.ForeignKey(Company, models.PROTECT, null=True, related_name='transaction')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT, related_name='user_transaction', null=True)
    participant = models.ForeignKey(InvestmentParticipation, models.PROTECT, null=True)
    partner_code = models.TextField(null=True, help_text='MOMOTW0N20220620')
    order_id = models.TextField(null=True)
    request_id = models.TextField(null=True)
    amount = models.IntegerField(null=True)
    order_info = models.TextField(null=True)
    order_type = models.TextField(null=True)
    trans_id = models.TextField(null=True)
    result_code = models.TextField(null=True)
    message = models.TextField(default=EMPTY_TRANSACTION)
    pay_type = models.TextField(null=True)
    response_time = models.TextField(null=True)
    extra_data = models.JSONField(null=True)
    signature = models.TextField(null=True)

    class Meta:
        db_table = 'transaction_history_list'


class CryptoPaymentTransaction(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    company = models.ForeignKey(Company, models.PROTECT, null=True, related_name='crypto_transaction')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT, related_name='user_crypto_transaction',
                             null=True)
    participant = models.ForeignKey(InvestmentParticipation, models.PROTECT, null=True)
    platform = models.TextField()
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    currency = models.TextField()
    transaction_type = models.TextField()
    prepay_order_id = models.TextField()
    status = models.TextField()

    class Meta:
        db_table = 'crypto_history_list'


class CryptoPaymentEventLog(models.Model):
    bizType = models.TextField()
    data = models.JSONField(default=dict, null=True)
    bizId = models.TextField()
    bizStatus = models.TextField()

    class Meta:
        db_table = 'binance_event'


class MomoIntegrationInformation(models.Model):
    partner_code = models.TextField(null=True)
    access_key = models.TextField(null=True)
    secret_key = models.TextField(null=True)

    @property
    def camel_case_info(self):
        return {
            'partnerCode': self.partner_code,
            'accessKey': self.access_key,
            'secretKey': self.secret_key,
        }

    class Meta:
        db_table = 'momo_integration_info'
