import readtime
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.utils.text import slugify

from apps.media_center.models import Media
from utils.models import UuidModelMixin

"""
WebLog Models
"""
from django.db.models import UniqueConstraint


class BlogCategoryManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class BlogCategory(UuidModelMixin, models.Model):
    name = models.TextField(unique=True)
    order = models.IntegerField(validators=[MaxValueValidator(100), MinValueValidator(1)], default=1)
    is_active = models.BooleanField(
        default=True,
    )
    slug = models.SlugField(null=True)
    objects = BlogCategoryManager()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, allow_unicode=True)
        super(BlogCategory, self).save(*args, **kwargs)

    def natural_key(self):
        return self.name

    class Meta:
        db_table = 'blog_category'
        ordering = 'id',
        constraints = [
            UniqueConstraint(
                Lower('name'),
                name='category_name_unique',
            ),
        ]


class BlogPost(UuidModelMixin, models.Model):
    OPEN = 'open'
    CLOSE = 'close'
    PUBLISH = 'publish'
    DRAFT = 'draft'
    POST_STATUS = (
        (PUBLISH, PUBLISH),
        (DRAFT, DRAFT)

    )
    COMMENT_STATUS = (
        (OPEN, OPEN),
        (CLOSE, CLOSE),
    )

    author = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    title = models.TextField(unique=True)
    category = models.ForeignKey(BlogCategory, models.PROTECT)
    excerpt = models.TextField()
    raw_content = models.TextField()
    content = models.TextField()

    header_image = models.ForeignKey(Media, models.SET_NULL, null=True)

    post_status = models.CharField(max_length=100, choices=POST_STATUS)
    comment_status = models.CharField(max_length=100, choices=COMMENT_STATUS)

    tags = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, null=True)

    @property
    def read_time(self):
        result = readtime.of_text(self.raw_content)
        return f'{result.text} read'

    def save(self, *args, **kwargs):
        # if not self.slug:
        self.slug = slugify(self.title, allow_unicode=True)
        super(BlogPost, self).save(*args, **kwargs)

    class Meta:
        db_table = 'learning_blogpost'
        ordering = '-created_at',


class BlogPostComment(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT, related_name='user_blogpost_comments')
    post = models.ForeignKey(BlogPost, models.PROTECT, related_name='blogpost_comments')
    parent_comment = models.ForeignKey('self', models.PROTECT, related_name='comment_reply', null=True)

    class Meta:
        db_table = 'learning_blogpost_comment'
        ordering = '-created_at',


class BlogPostLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT, related_name='user_blogpost_likes')
    post = models.ForeignKey(BlogPost, models.PROTECT, related_name='blogpost_likes')
    like = models.IntegerField(validators=[
        MaxValueValidator(1),
        MinValueValidator(0)
    ])

    class Meta:
        db_table = 'learning_blogpost_like'


class BlogPostCommentLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT, related_name='user_blogpost_comment_likes')
    comment = models.ForeignKey(BlogPostComment, models.PROTECT, related_name='blogpost_comment_likes')
    like = models.IntegerField(validators=[
        MaxValueValidator(1),
        MinValueValidator(0)
    ])

    class Meta:
        db_table = 'learning_blogpost_comment_like'


#
#
"""
Podcast and Events
"""


class Podcast(models.Model):
    title = models.TextField()
    subtitle = models.TextField()
    content = models.TextField()

    header_image = models.ForeignKey(Media, models.SET_NULL, null=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    listen_on = models.JSONField()

    class Meta:
        db_table = 'learning_Podcast'


class Event(models.Model):
    title = models.TextField()
    excerpt = models.TextField()
    content = models.TextField()
    raw_content = models.TextField()
    header_image = models.ForeignKey(Media, models.SET_NULL, null=True, related_name='event_header_photo')
    execution_date_start = models.DateTimeField(null=True)
    execution_date_end = models.DateTimeField(null=True)
    location = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'learning_event'


"""
Frequently asked questions
"""


class FrequentlyAskedQuestionCategoryManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


# TODO add created_at,modified_at  to all models
class FrequentlyAskedQuestionCategory(models.Model):
    name = models.TextField()
    order = models.IntegerField(validators=[MaxValueValidator(100), MinValueValidator(1)], default=1)
    is_active = models.BooleanField(default=True, )
    slug = models.SlugField(null=True)
    objects = FrequentlyAskedQuestionCategoryManager()

    def natural_key(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, allow_unicode=True)
        super(FrequentlyAskedQuestionCategory, self).save(*args, **kwargs)

    class Meta:
        db_table = 'faq_category'
        ordering = 'id',


class FrequentlyAskedQuestion(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    title = models.TextField()
    category = models.ForeignKey(FrequentlyAskedQuestionCategory, models.PROTECT)
    content = models.TextField()
    raw_content = models.TextField()

    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'faq_question'
        ordering = 'id',
