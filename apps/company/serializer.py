import copy

from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers

from utils.serializers import get_model_fields
from .models import Company, CompanyDetails, CompanyPresent, CompanyPresentDetails, CompanyPresentDocuments, \
    CompanyPresentCategory, CompanyPresentTeamMember
from ..dashboard.serializers import QuestionSerializer, QuestionDefaultAnswerSerializer
from ..media_center.serialzer import media_expandable_fields


class CompanySerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Company
        fields = [
                     'id',
                     'entrepreneur_name',
                     'created_at',
                     'company_name',
                     'website',
                     'email',
                     'address',
                     'phone_number',
                     'registration_docs',
                     'github',
                     'tax_receipt',
                     'intro_video',
                     'status'
                 ] + ['has_company_present']
        expandable_fields = {
            'tax_receipt': media_expandable_fields,
            'intro_video': media_expandable_fields,
            'registration_docs': media_expandable_fields,
        }
        read_only_fields = [
            'has_company_present',
            'created_at'
        ]


class CompanyDetailsSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = CompanyDetails
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

        # expandable_fields = {
        #     'attachment': media_expandable_fields,
        #     'question': (
        #         QuestionSerializer,
        #         {'many': False, 'fields': [
        #             'question_class',
        #             'order',
        #             'text',
        #             'text_vi',
        #             'hint'
        #         ]}
        #     ),
        #     'selected_answer': (
        #         QuestionDefaultAnswerSerializer,
        #         {'many': False, 'fields': [
        #             'answer_text',
        #             'answer_text_vi'
        #
        #         ]}
        #     ),
        # }


class FullCompanyDetailsSerializer(serializers.Serializer):
    company_profile = CompanySerializer(many=False, allow_null=False, omit=['user'])
    company_details = CompanyDetailsSerializer(many=True, allow_null=False, allow_empty=False, omit=['company'])

    def create(self, validated_data):
        print('FullCompanyDetailsSerializer create')
        user_id = validated_data.pop('user_id')

        validated_data_copy = copy.deepcopy(validated_data)
        investment_info_serializer = self.fields['company_details']
        profile_serializer = self.fields['company_profile']
        profile_data = validated_data_copy.get('company_profile')
        profile_data['user_id'] = user_id
        investment_info_data = validated_data_copy.get('company_details')
        instance = profile_serializer.create(profile_data)
        for item in investment_info_data:
            item['company_id'] = instance.id
        investment_info_serializer.create(investment_info_data)
        validated_data['company_profile'] = instance
        return validated_data


class CompanyPresentDetailsSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = CompanyPresentDetails
        fields = '__all__'


class CompanyPresentTeamMemberSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = CompanyPresentTeamMember
        fields = '__all__'
        expandable_fields = {
            'image': media_expandable_fields
        }


class CompanyPresentDocumentsSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = CompanyPresentDocuments
        fields = '__all__'
        expandable_fields = {
            'file': media_expandable_fields
        }


class CompanyPresentCategorySerializer(FlexFieldsModelSerializer):
    class Meta:
        model = CompanyPresentCategory
        fields = '__all__'


class CompanyPresentSerializer(FlexFieldsModelSerializer):
    present_details = CompanyPresentDetailsSerializer(many=True, omit=['company'], write_only=True)
    present_document = CompanyPresentDocumentsSerializer(many=True, write_only=True)
    present_team_member = CompanyPresentTeamMemberSerializer(many=True, omit=['company'], write_only=True)

    def create(self, validated_data):
        present_details = validated_data.pop('present_details', None)
        present_document = validated_data.pop('present_document', None)
        present_team_member = validated_data.pop('present_team_member', None)
        instance = super(CompanyPresentSerializer, self).create(validated_data)
        if present_details:
            present_details_serializer = self.fields['present_details']
            for item in present_details:
                item['company'] = instance
            present_details_serializer.create(present_details)

        if present_document:
            present_document_serializer = self.fields['present_document']
            for item in present_document:
                item['company'] = instance
            present_document_serializer.create(present_document)

        if present_team_member:
            present_team_member_serializer = self.fields['present_team_member']
            for item in present_team_member:
                item['company'] = instance
            present_team_member_serializer.create(present_team_member)
        return instance

    class Meta:
        model = CompanyPresent
        fields = get_model_fields(CompanyPresent) + (
            'collected_budget', 'present_details', 'present_document', 'present_team_member', 'number_investors')
        expandable_fields = {
            'logo_image': media_expandable_fields,
            'cover_image': media_expandable_fields,
            'cover_image_1': media_expandable_fields,
            'cover_image_2': media_expandable_fields,
            'company_category': (
                CompanyPresentCategorySerializer,
                {'many': False}
            ),
            'company_present_team_member': (
                CompanyPresentTeamMemberSerializer,
                {'many': True}
            ),
            'present_details': (
                CompanyPresentDetailsSerializer,
                {'many': True}
            ),
            'present_documents': (
                CompanyPresentDocumentsSerializer,
                {'many': True}
            ),
        }
