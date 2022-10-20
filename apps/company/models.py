import random
import uuid

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from apps.company.queryset import CompanyManager
from apps.dashboard.models import Question
from apps.media_center.models import Media


class Company(models.Model):
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
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT, related_name='user_company')
    company_name = models.TextField(unique=True)
    entrepreneur_name = ArrayField(base_field=models.CharField(max_length=100))
    website = models.TextField()
    email = models.TextField()
    address = models.TextField()
    phone_number = models.TextField()
    youtube_url = models.TextField(null=True, blank=True)
    registration_docs = models.ForeignKey(Media, models.SET_NULL, related_name='register_doc_media', null=True)
    registration_docs_1 = models.ForeignKey(Media, models.SET_NULL, related_name='register_doc_media_1', null=True)
    registration_docs_2 = models.ForeignKey(Media, models.SET_NULL, related_name='register_doc_media_2', null=True)
    github = models.TextField(null=True, blank=True)
    tax_receipt = models.ForeignKey(Media, models.SET_NULL, related_name='tax_doc_media', null=True)
    intro_video = models.ForeignKey(Media, models.SET_NULL, related_name='intro_video_media', null=True)
    objects = CompanyManager()

    @property
    def has_company_present(self):
        user_count = self.company_present.count()
        return True if user_count > 0 else False

    class Meta:
        db_table = 'company'
        ordering = 'id',


class CompanyDetails(models.Model):
    company = models.ForeignKey(Company, models.PROTECT, related_name='company_details')
    question = models.ForeignKey(Question, models.PROTECT, )
    answer_text = ArrayField(models.TextField())
    attachment = models.ForeignKey(Media, models.SET_NULL, related_name='company_details_media', null=True)

    class Meta:
        db_table = 'company_details'
        ordering = 'id',


class CompanyPresentCategory(models.Model):
    name = models.TextField()

    class Meta:
        db_table = 'company_present_category'
        ordering = 'id',


class CompanyPresent(models.Model):
    APPROVED = 'approved'
    REJECTED = 'rejected'
    PENDING = 'pending'
    STATUS = (
        (APPROVED, APPROVED),
        (REJECTED, REJECTED),
        (PENDING, PENDING),
    )

    status = models.CharField(max_length=100, choices=STATUS, default=PENDING)
    """
        Admin Control fields
    """

    is_trending = models.BooleanField(default=True)
    is_hot = models.BooleanField(default=True)

    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name='company_present')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    """
    Preview Fields
    """
    cover_image = models.ForeignKey(Media, models.PROTECT, related_name='company_present_preview', null=True)
    cover_image_1 = models.ForeignKey(Media, models.PROTECT, related_name='company_present_preview_1', null=True)
    cover_image_2 = models.ForeignKey(Media, models.PROTECT, related_name='company_present_preview_2', null=True)
    #cover_image1 = models.ForeignKey(Media, models.PROTECT, related_name='company_present_preview1', null=True)
    #cover_image2 = models.ForeignKey(Media, models.PROTECT, related_name='company_present_preview2', null=True)
    youtube_url = models.TextField(null=True)
    youtubeUrl = models.TextField(null=True)
    logo_image = models.ForeignKey(Media, models.PROTECT, related_name='company_present_logo', null=True)
    company_name = models.TextField()
    company_sub_title = models.TextField()
    abstract = models.TextField()
    company_category = models.ForeignKey(CompanyPresentCategory, models.PROTECT,
                                         related_name='company_present_category',
                                         null=True)
    """
    company about Info
    """
    founded = models.DateField()
    employees = models.IntegerField(null=True)
    website = models.TextField(null=True)
    email = models.EmailField(null=True)
    phone_number = models.TextField(null=True)
    location = models.TextField(null=True)
    facebook = models.TextField(null=True)
    twitter = models.TextField(null=True)
    linkedin = models.TextField(null=True)
    instagram = models.TextField(null=True)
    youtube = models.TextField(null=True)

    """
    Summery Value Fields
    """
    investment_min = models.IntegerField()
    investment_target = models.IntegerField()

    price_per_share = models.DecimalField(max_digits=30, decimal_places=4, null=True)
    shares_offered = models.TextField(null=True)
    offering_type = models.TextField(null=True)
    closing_date = models.DateField(null=True)

    @property
    def collected_budget(self):
        return int(self.investment_target * 40 / 100)

    @property
    def number_investors(self):
        return int(self.investment_target * 0.5 / 100)

    class Meta:
        db_table = 'company_present'
        ordering = 'id',


class CompanyPresentTeamMember(models.Model):
    name = models.TextField()
    position = models.TextField()
    about = models.TextField()
    linkedin = models.TextField()
    image = models.ForeignKey(Media, models.SET_NULL, related_name='company_present_team_member', null=True)
    company = models.ForeignKey(CompanyPresent, models.SET_NULL, related_name='company_present_team_member', null=True)

    class Meta:
        db_table = 'company_present_team_member'
        ordering = 'id',


class CompanyPresentDetails(models.Model):
    company = models.ForeignKey(CompanyPresent, models.CASCADE, null=True, related_name='present_details')
    title = models.TextField()
    details = models.TextField()

    class Meta:
        db_table = 'company_present_details'
        ordering = 'id',


class CompanyPresentDocuments(models.Model):
    company = models.ForeignKey(CompanyPresent, models.CASCADE, null=True, related_name='present_documents')
    file = models.ForeignKey(Media, models.CASCADE, null=True, related_name='present_document')
    file_name = models.TextField()

    class Meta:
        db_table = 'company_present_documents'
        ordering = 'id',


class CompanyPresentHeaderSlider(models.Model):
    resource = models.ForeignKey(Media, models.CASCADE, related_name='company_present_header_slider')
    company_present = models.ForeignKey(Media, models.CASCADE)
    order = models.IntegerField(validators=[MaxValueValidator(100), MinValueValidator(1)])

    class Meta:
        db_table = 'company_present_header_slider'
        ordering = 'id',
