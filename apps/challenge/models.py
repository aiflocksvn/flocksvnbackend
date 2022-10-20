from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models

from apps.media_center.models import Media


class ChallengeDay(models.Model):
    day_number = models.IntegerField()
    # name = models.TextField(null=True)
    # name_vi = models.TextField(null=True)
    icon = models.ImageField(upload_to='public/')

    # def __str__(self):
    #     return f'{self.name}'

    class Meta:
        db_table = 'challenge_day'
        ordering = 'day_number',


class Challenge(models.Model):
    title = models.TextField()
    title_vi = models.TextField(null=True)
    description = models.TextField()
    description_vi = models.TextField()
    challenge_day = models.ForeignKey(ChallengeDay, models.CASCADE, related_name='challenge')

    @property
    def number_of_question(self):
        return self.challenge_question.all().count()

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'challenge'


class ChallengeQuestion(models.Model):
    QUESTION_ANSWER = 'question_answer'
    ATTACHMENT = 'attachment'
    LINK = 'link'
    CHALLENGE_TYPE = (
        (LINK, LINK),
        (ATTACHMENT, ATTACHMENT),
        (QUESTION_ANSWER, QUESTION_ANSWER),
    )

    INPUT_TEXT = 'input_text'
    SINGLE_CHOICE = 'single_choice'
    BOOLEAN = 'boolean'
    QUESTION_TYPE = (
        (INPUT_TEXT, INPUT_TEXT),
        (BOOLEAN, BOOLEAN),
        (SINGLE_CHOICE, SINGLE_CHOICE),
    )
    title = models.TextField()
    challenge_type = models.CharField(choices=CHALLENGE_TYPE, max_length=100)
    question_type = models.CharField(choices=QUESTION_TYPE, max_length=100)
    title_vi = models.TextField(null=True)
    hint = models.TextField(null=True)
    hint_vi = models.TextField(null=True)
    challenge = models.ForeignKey(Challenge, models.CASCADE, related_name='challenge_question')
    answer_text = ArrayField(models.JSONField(), null=True)

    class Meta:
        db_table = 'challenge_question'


class ChallengeResult(models.Model):
    PENDING = 'pending'
    FAILED = 'failed'
    PASSES = 'passed'
    LOCK = 'LOCK'
    OPENING = 'OPEN'
    CHALLENGE_STATUS = (
        (PASSES, PASSES),
        (PENDING, PENDING),
        (FAILED, FAILED)
    )
    result = models.CharField(max_length=100, choices=CHALLENGE_STATUS, default=PENDING)
    challenge = models.ForeignKey(Challenge, models.CASCADE, related_name='challenge_result')
    # day = models.ForeignKey(Challenge, models.CASCADE, related_name='challenge_day')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT, related_name='user_challenge_ans', null=True)

    @property
    def challenge_day(self):
        return self.challenge.challenge_day.day_number

    class Meta:
        db_table = 'challenge_result'


class ChallengeQuestionAnswer(models.Model):
    question = models.ForeignKey(ChallengeQuestion, models.CASCADE)
    challenge_result = models.ForeignKey(ChallengeResult, models.CASCADE, related_name='challenge_user_answer')
    answer = models.TextField(null=True)
    attachment = models.ForeignKey(Media, models.SET_NULL, related_name='challenge_ans_attach', null=True)

    class Meta:
        db_table = 'challenge_user_answer'
