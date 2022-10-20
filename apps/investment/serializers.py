import copy

from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers

from utils.exceptions import DuplicateInvestmentError
from .models import InvestmentProfile, InvestmentDetails, InvestmentParticipation
from ..authentication.models import SystemUser
from ..dashboard.serializers import QuestionDefaultAnswerSerializer, QuestionSerializer


class InvestmentDetailsSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = InvestmentDetails
        fields = '__all__'

        expandable_fields = {
            'question': (
                QuestionSerializer,
                {'many': False, 'fields': [
                    'question_class',
                    'priority',
                    'text',
                    'text_vi',
                    'hint'
                ]}
            ),
            'selected_answer': (
                QuestionDefaultAnswerSerializer,
                {'many': False, 'fields': [
                    'answer_text',
                    'answer_text_vi'

                ]}
            ),
        }


class InvestProfileSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = InvestmentProfile
        fields = '__all__'
        expandable_fields = {
            'invest_extra_info': (
                InvestmentDetailsSerializer,
                {'many': True, 'fields': [
                    'question',
                    'answer_text',
                    'selected_answer'
                ]}
            ),
        }


class FullInvestmentProfileSerializer(serializers.Serializer):
    investment_profile = InvestProfileSerializer(many=False, allow_null=False, omit=['user'])
    investment_details = InvestmentDetailsSerializer(many=True, allow_null=False, allow_empty=False)

    # def validate(self, attrs):
    #     user = attrs.get('user')
    #     if user.has_investment_profile:
    #         raise DuplicateInvestmentError
    #     return attrs

    def create(self, validated_data):
        user = validated_data.pop('user')
        user_id = user.id
        if user.has_investment_profile:
            raise DuplicateInvestmentError
        validated_data_copy = copy.deepcopy(validated_data)
        investment_info_serializer = self.fields['investment_details']
        profile_serializer = self.fields['investment_profile']
        profile_data = validated_data_copy.get('investment_profile')
        profile_data['user_id'] = user_id
        investment_info_data = validated_data_copy.get('investment_details')
        instance = profile_serializer.create(profile_data)
        for item in investment_info_data:
            item['invest_id'] = instance
        investment_info_serializer.create(investment_info_data)
        return validated_data


class InvestmentParticipationSerializer(FlexFieldsModelSerializer):
    # payment_token = serializers.CharField(write_only=True, required=True)
    redirect_url = serializers.CharField(write_only=True, required=False,
                                         default='https://webhook.site/b3088a6a-2d17-4f8d-a383-71389a6c600b')

    def create(self, validated_data):
        validated_data.pop('redirect_url')
        # card_token_id = validated_data.pop('payment_token')
        # invest_amount = validated_data['investment_amount']
        # customer: SystemUser = validated_data['investor']
        # company = validated_data['company']
        # create_payment_request
        # StripePayment.create_source_with_charge(amount=invest_amount, card_token_id=card_token_id,
        #                                         customer_id=customer.stripe_customer_account().id,
        #                                         meta_data={
        #                                             'company_id': str(company.id),
        #                                             'company_name': str(company.company_name)
        #
        #                                         }
        #
        #                                         )
        instance = super(InvestmentParticipationSerializer, self).create(validated_data)
        return instance

    class Meta:
        model = InvestmentParticipation
        fields = '__all__'
        read_only_fields = ['investor']
