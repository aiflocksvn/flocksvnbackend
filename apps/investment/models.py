from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from apps.company.models import Company
from apps.dashboard.models import Question
from apps.investment.queryset import InvestorManager
from apps.media_center.models import Media

"""
Investment Profile 
"""


class InvestmentProfile(models.Model):
    APPROVED = 'approved'
    REJECTED = 'rejected'
    PENDING = 'pending'
    STATUS = (
        (APPROVED, APPROVED),
        (REJECTED, REJECTED),
        (PENDING, PENDING),
    )
    status = models.CharField(max_length=100, choices=STATUS, default=PENDING)
    created_at = models.DateTimeField(default=timezone.now)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, models.PROTECT, related_name='invest_profile')
    investor_id_number = models.TextField()
    investor_name = models.TextField()
    investor_email = models.TextField()
    investor_address = models.TextField()
    investor_phone = models.TextField()
    objects = InvestorManager()

    class Meta:
        db_table = 'investment_profile'
        ordering = 'id',


"""
Investment More Information  
"""


class InvestmentDetails(models.Model):
    invest_id = models.ForeignKey(InvestmentProfile, models.PROTECT, null=True, related_name='invest_details')
    question = models.ForeignKey(Question, models.PROTECT)
    answer_text = ArrayField(models.TextField())
    attachment = models.ForeignKey(Media, models.SET_NULL, related_name='investment_details_media', null=True)

    class Meta:
        db_table = 'investment_details'
        ordering = 'id',


class InvestmentParticipation(models.Model):
    company = models.ForeignKey(Company, models.PROTECT, related_name='investment_participation')
    investor = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT, related_name='participated_companies')
    investment_amount = models.IntegerField(validators=[MaxValueValidator(50000000), MinValueValidator(10000)])

    class Meta:
        db_table = 'investment_participation'
