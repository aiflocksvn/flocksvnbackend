# Create your models here.

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

from apps.media_center.models import Media
from utils.models import UuidModelMixin


class IdentityVerification(UuidModelMixin, models.Model):
    PRE_PENDING = 'pre_pending'
    DONE = 'done'
    FAILED = 'failed'
    FINAL_VERIFICATION_STATUS = (
        (PRE_PENDING, PRE_PENDING),
        (DONE, DONE),
        (FAILED, FAILED),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, models.PROTECT, related_name='identity')
    created_at = models.DateTimeField(auto_now=True, editable=False, null=True)

    verification_status = models.CharField(max_length=100, null=True, choices=FINAL_VERIFICATION_STATUS,
                                           default=PRE_PENDING)
    service_data = models.JSONField(default=dict, null=True)
    failed_reason = models.TextField(null=True)
    selfie_photo = models.ForeignKey(Media, models.PROTECT, null=True, related_name='identity_selfie')
    card_front = models.ForeignKey(Media, models.PROTECT, null=True, related_name='identity_card_front')
    card_back = models.ForeignKey(Media, models.PROTECT, null=True, related_name='identity_card_back')

    class Meta:
        ordering = 'id',


class QuestionClass(models.Model):
    INVESTMENT = 'investment'
    COMPANY = 'company'

    RELATED = (
        (INVESTMENT, INVESTMENT),
        (COMPANY, COMPANY),
    )
    name = models.TextField()
    name_vi = models.TextField()
    order = models.IntegerField(validators=[MaxValueValidator(100), MinValueValidator(1)])
    related_to = models.CharField(RELATED, max_length=100)
    is_active = models.BooleanField(default=True)

    @property
    def question_count(self):
        return self.question_set.count()

    class Meta:
        db_table = 'question_class'
        ordering = ('related_to', 'order')
        # unique_together = [['name', 'related_to']]


class Question(models.Model):
    WIDGET_TYPE = (
        ('slider', 'slider'),
        ('input_number', 'input_number'),
        ('input_text', 'input_text'),
        ('single_choice', 'single_choice'),
        ('multiple_choice', 'multiple_choice'),
        ('dropdown', 'dropdown'),
    )

    is_active = models.BooleanField(default=True)
    widget_type = models.CharField(max_length=100, choices=WIDGET_TYPE)
    code = models.CharField(editable=False, max_length=200, default='')
    question_class = models.ForeignKey(QuestionClass, models.PROTECT)
    text = models.TextField()
    text_vi = models.TextField(null=True)
    hint = models.TextField(null=True)
    hint_vi = models.TextField(null=True)
    order = models.IntegerField(validators=[MaxValueValidator(100), MinValueValidator(1)], null=True)

    class Meta:
        db_table = 'question'
        ordering = 'order', 'pk'
        # unique_together = [['order', 'question_class']]


class QuestionDefaultAnswer(models.Model):
    question = models.ForeignKey(Question, models.CASCADE, related_name='default_answer_set')
    answer_text = models.TextField()
    answer_text_vi = models.TextField(null=True)

    class Meta:
        db_table = 'question_default_answer'
        ordering = 'id',
