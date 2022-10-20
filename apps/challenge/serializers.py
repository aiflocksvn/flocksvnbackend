from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers

from utils.serializers import get_model_fields
from .models import ChallengeDay, Challenge, ChallengeQuestion, ChallengeResult \
    , ChallengeQuestionAnswer
from ..authentication.models import SystemUser
from ..authentication.serializers import user_expandable_fields
from ..media_center.serialzer import media_expandable_fields


class ChallengeDaySerializer(FlexFieldsModelSerializer):
    challenge_icon = serializers.SerializerMethodField()
    day_status = serializers.SerializerMethodField()

    def get_day_status(self, obj: ChallengeDay):
        user = self.context['request'].user
        result = ''
        try:
            result = ChallengeResult.objects.filter(challenge__challenge_day_id=obj.id, user=user).first().result
            # return result
        except AttributeError:
            try:
                last_day = ChallengeResult.objects.filter(user=user).order_by(
                    '-challenge__challenge_day_id').first().challenge_day
                if last_day + 1 == obj.day_number:
                    result = ChallengeResult.OPENING
                else:
                    result = ChallengeResult.LOCK
            except AttributeError:
                if obj.day_number == 1:
                    result = ChallengeResult.OPENING
        return result

    def get_challenge_icon(self, obj: ChallengeDay):
        return obj.icon.url

    class Meta:
        model = ChallengeDay
        fields = get_model_fields(model) + ('day_status', 'challenge_icon')
        extra_kwargs = {
            'icon': {
                'write_only': True
            },
        }


class ChallengeQuestionSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = ChallengeQuestion
        fields = '__all__'


class ChallengeUpdateSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Challenge
        fields = get_model_fields(model)


class ChallengeSerializer(FlexFieldsModelSerializer):
    questions = ChallengeQuestionSerializer(write_only=True, omit=['challenge'], many=True, allow_empty=False,
                                            allow_null=False)

    def create(self, validated_data):
        questions = validated_data.pop('questions')
        challenge = super(ChallengeSerializer, self).create(validated_data)

        if questions:
            for qs in questions:
                qs['challenge'] = challenge
            question_serializer = self.fields['questions']
            question_serializer.create(questions)
        return validated_data

    class Meta:
        model = Challenge
        fields = get_model_fields(model) + ('number_of_question', 'questions')

    expandable_fields = {
        'challenge_question': (
            ChallengeQuestionSerializer,
            {'many': True}
        ),
    }


class ChallengeQuestionAnswerSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = ChallengeQuestionAnswer
        fields = get_model_fields(model)
        expandable_fields = {
            'question': (
                ChallengeQuestionSerializer,
                {'many': False}
            ),
        }


class ChallengeResultSerializer(FlexFieldsModelSerializer):
    answers = ChallengeQuestionAnswerSerializer(write_only=True, omit=['challenge_result'], many=True,
                                                allow_empty=False,
                                                allow_null=False)

    # challenge_day = serializers.SerializerMethodField()

    # def get_challenge_day(self, obj: ChallengeResult):
    #     return obj.challenge.challenge_day.day_number

    def create(self, validated_data):
        answers = validated_data.pop('answers')
        print(answers)
        instance = super(ChallengeResultSerializer, self).create(validated_data)
        if answers:
            for ans in answers:
                ans['challenge_result'] = instance
            answers_serializer = self.fields['answers']
            answers_serializer.create(answers)
        return validated_data

    class Meta:
        model = ChallengeResult
        # fields = get_model_fields(model) + ('answers', 'challenge_day')
        fields = get_model_fields(model) + ('answers',)
        read_only_fields = ['result', 'user']
        expandable_fields = {
            'user': user_expandable_fields,
            'challenge_user_answer': (
                ChallengeQuestionAnswerSerializer,
                {'many': True}
            ),
            'challenge': (
                ChallengeSerializer,
                {'many': False}
            ),
        }


class UserWithChallengeSerializer(FlexFieldsModelSerializer):
    failed_challenge = serializers.IntegerField()
    passed_challenge = serializers.IntegerField()

    class Meta:
        model = SystemUser
        fields = get_model_fields(model) + ('failed_challenge', 'passed_challenge')
        expandable_fields = {
            'avatar': media_expandable_fields,
            # 'cover_photo': media_expandable_fields,
        }
