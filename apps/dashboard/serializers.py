from django.contrib.auth import authenticate
from django.template.loader import render_to_string
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework_api_key.models import APIKey
from django.utils.translation import gettext_lazy as _
from apps.authentication.models import SystemUser
from apps.authentication.serializers import user_expandable_fields
from apps.dashboard.models import IdentityVerification, QuestionDefaultAnswer, Question, QuestionClass
from apps.system_settings.models import SystemOption, SmtpConfig
from utils.exceptions import AuthenticationFailed
from utils.maile import send_mail
from utils.request_utils import ip_details

# from rest_framework.exceptions import AuthenticationFailed

"""
WebSite Serialzier
"""


class ContactFormSerializer(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.EmailField()
    subject = serializers.CharField()
    message = serializers.CharField()

    def dict_to_tab_space(self, data):
        table = ''
        for key, value in data.items():
            table += "{0} {1} {2:^40}\n".format(key, ':', value)
        return table

    def create_mail_connection(self, request, validated_data):
        admin_mail = SystemOption.objects.contact_mail_address().option_value
        credential = SmtpConfig.objects.info_mail().normalized_config()
        details = ip_details(request)
        # detail = self.dict_to_tab_space(details)

        data = {**validated_data, 'extra_data': details}

        email_html_message = render_to_string('email/user_contact_form.html', data)
        send_mail(credential, subject=validated_data.get('subject'), recipient_list=[admin_mail],
                  email_html_message=email_html_message)

    def create(self, validated_data):
        self.create_mail_connection(self.context['request'], validated_data)
        # threading.Thread(target=self.create_mail_connection, args=(user,)).start()
        return validated_data


class VerificationSerializer(serializers.Serializer):
    liveness_img = serializers.ImageField()
    front_img = serializers.ImageField()
    back_img = serializers.ImageField(allow_null=True, required=False)

    # def validate(self, attrs):
    #     print(attrs)
    #     return attrs


class VerificationStatusSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = IdentityVerification
        fields = '__all__'
        expandable_fields = {
            'user': user_expandable_fields
        }


class QuestionDefaultAnswerSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = QuestionDefaultAnswer
        fields = '__all__'
        read_only_fields = ['question']


class QuestionSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'
        expandable_fields = {
            'default_answer_set': (
                QuestionDefaultAnswerSerializer,
                {'many': True, 'fields': [
                    'id',
                    'answer_text',
                    'answer_text_vi'
                ]}
            ),
            'question_class': (
                'apps.dashboard.QuestionClassSerializer',
                {'many': False, 'fields': [
                    'id',
                    'name',
                    'name_vi',
                    'order',
                    'related_to',
                    'is_active',
                    'question_count'
                ]}
            ),
        }


class QuestionClassSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = QuestionClass
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=QuestionClass.objects.all(),
        #         fields=['name', 'related_to']
        #     )
        # ]
        # read_only_fields = ['related_to']

        fields = [
            'id',
            'name',
            'name_vi',
            'order',
            'related_to',
            'is_active',
            'question_count'

        ]
        expandable_fields = {
            'question_set': (
                QuestionSerializer,
                {'many': True, 'fields': [
                    'id',
                    'question_is_active',
                    'widget_type',
                    'question_code',
                    'question_text',
                    'question_text_vi',
                    'question_hint',
                    'question_hint_vi',

                ]}
            ),
        }


"""
Dashboard Auth
"""


class QuestionCreateSerializer(FlexFieldsModelSerializer):
    default_answers = QuestionDefaultAnswerSerializer(many=True, omit=['question'], required=False, allow_null=False,
                                                      allow_empty=False, write_only=True)

    def create(self, validated_data):
        print('sadfasdfasd fasd fasdf sdf')
        # print('salsdfsf')
        default_answers = validated_data.pop('default_answers', None)
        instance = super(QuestionCreateSerializer, self).create(validated_data)
        print(default_answers)
        print(instance)
        if default_answers:
            default_answers = list(map(lambda p: QuestionDefaultAnswer(**p, question=instance), default_answers))
            QuestionDefaultAnswer.objects.bulk_create(default_answers)
        return validated_data

    class Meta:
        model = Question
        fields = [
            'is_active',
            'widget_type',
            'code',
            'question_class',
            'text',
            'text_vi',
            'hint',
            'hint_vi',
            'order',
            'default_answers'

        ]


"""
Bulk Update
"""


class QuestionDefaultAnswerEmbedIDUpdateListSerializer(serializers.ListSerializer):

    def bulkupdate(self, validated_data):
        for item in validated_data:
            QuestionDefaultAnswer.objects.filter(id=item.pop('id')).update(**item)
        return validated_data


class QuestionDefaultAnswerEmbedIDUpdateSerializer(FlexFieldsModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = QuestionDefaultAnswer
        fields = ['answer_text', 'answer_text_vi', 'id']
        list_serializer_class = QuestionDefaultAnswerEmbedIDUpdateListSerializer


class DefaultAwnserBuklkUpdateSerializer(serializers.Serializer):
    def save(self, validated_data, instance_pk):
        deleted_items = validated_data.get('deleted_items')
        created_item = validated_data.get('created_items')
        update_item = validated_data.get('updated_items')

        if deleted_items:
            QuestionDefaultAnswer.objects.filter(pk__in=[item.pk for item in deleted_items]).delete()
        if created_item:
            item_set_serializer = self.fields['created_items']
            for item in created_item:
                item['question'] = instance_pk
            item_set_serializer.create(created_item)
        if update_item:
            item_set_serializer = self.fields['updated_items']
            item_set_serializer.bulkupdate(update_item)
        return validated_data

    deleted_items = serializers.PrimaryKeyRelatedField(required=False, many=True,
                                                       queryset=QuestionDefaultAnswer.objects.all(),
                                                       allow_null=False,
                                                       allow_empty=False
                                                       )
    updated_items = QuestionDefaultAnswerEmbedIDUpdateSerializer(
        many=True,
        allow_null=False,
        allow_empty=False,
        required=False
    )
    created_items = QuestionDefaultAnswerSerializer(
        # id_required=False,
        many=True,
        allow_null=False,
        allow_empty=False,
        required=False
    )


class QuestionUpdateSerializer(FlexFieldsModelSerializer):
    default_answers = DefaultAwnserBuklkUpdateSerializer(many=False, required=False, allow_null=False,
                                                         write_only=True)

    def update(self, instance, validated_data):
        default_answers = validated_data.pop('default_answers', None)
        instance_pk = super().update(instance, validated_data)
        if default_answers:
            default_answers_serializer: DefaultAwnserBuklkUpdateSerializer = self.fields['default_answers']
            print(default_answers)
            print(default_answers_serializer)
            # default_answers_serializer.is_valid()
            default_answers_serializer.save(validated_data=default_answers, instance_pk=instance_pk)
        return validated_data

    class Meta:
        model = Question
        fields = [
            'is_active',
            'widget_type',
            'code',
            'question_class',
            'text',
            'text_vi',
            'hint',
            'hint_vi',
            'order',
            'default_answers'

        ]


"""
Dashboard Auth
"""


class AdminSignInSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=100, allow_null=True, required=False, allow_blank=True)

    def validate(self, data):
        email, password = data.get('email'), data.get('password')

        user = authenticate(username=email, password=password)
        user_role = getattr(user, 'role', None)
        if user:
            if user.is_dashboard_user and user_role:
                login_data = user.get_login_data()
                return login_data
        raise AuthenticationFailed


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    def update(self, instance: SystemUser, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.avatar = validated_data.get('avatar', instance.avatar)
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    class Meta:
        model = SystemUser
        fields = ['first_name', 'last_name', 'email', 'password', 'avatar']


"""
Api ky
"""

#
# class APIKeySerializer(serializers.ModelSerializer):
#     api_key = serializers.CharField(default=None, read_only=True)
#
#     def create(self, validated_data):
#         obj = APIKey(**validated_data)
#         key = APIKey.objects.assign_key(obj)
#         obj.save()
#         message = _(
#             "The API key for {} is: {}. ".format(obj.name, key)
#             + "Please store it somewhere safe: "
#             + "you will not be able to see it again."
#         )
#         validated_data['api_key'] = message
#         return validated_data
#
#     class Meta:
#         model = APIKey
#         fields = ['prefix', 'created', 'name', 'revoked', 'expiry_date', 'api_key']
#         read_only_fields = [
#             'id',
#             'prefix',
#             'hashed_key',
#             'api_key',
#
#         ]
#         extra_kwargs = {
#             'name': {
#                 'required': True
#             }
#         }
