from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers

from .models import OnlineTransaction
from ..authentication.models import SystemUser
from ..authentication.serializers import user_expandable_fields
from ..company.models import Company
from ..company.serializer import CompanySerializer
from ..investment.serializers import InvestmentParticipationSerializer
from .models import CryptoPaymentTransaction


class OnlineTransactionSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = OnlineTransaction
        fields = '__all__'
        read_only_fields = (
            'id',
            'company',
            'user',
            'participant',
        )
        expandable_fields = {
            'user': user_expandable_fields,
            'company': (
                CompanySerializer, {'many': False}
            ),
            'participant': (
                InvestmentParticipationSerializer, {'many': False}
            )
        }


class CryptoPaymentTransactionSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = CryptoPaymentTransaction
        fields = '__all__'
        read_only_fields = (
            'id',
            'company',
            'user',
            'participant',
        )
        expandable_fields = {
            'user': user_expandable_fields,
            'company': (
                CompanySerializer, {'many': False}
            ),
            'participant': (
                InvestmentParticipationSerializer, {'many': False}
            )
        }
