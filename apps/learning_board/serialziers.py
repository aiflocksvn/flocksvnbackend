from rest_flex_fields import FlexFieldsModelSerializer
from .models import Event
from apps.authentication.serializers import user_expandable_fields
from apps.learning_board.models import BlogPost, BlogCategory, FrequentlyAskedQuestionCategory, FrequentlyAskedQuestion
from apps.media_center.serialzer import media_expandable_fields
from rest_framework import serializers


class BlogPostCategorySerializer(FlexFieldsModelSerializer):
    class Meta:
        model = BlogCategory
        fields = '__all__'


class BlogPostSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = BlogPost
        fields = [
            'author',
            'created_at',
            'modified_at',
            'title',
            'category',
            'excerpt',
            'raw_content',
            'content',
            'header_image',

            'post_status',
            'comment_status',
            'tags',
            'slug',
            'read_time'

        ]
        read_only_fields = ['author', 'slug']
        expandable_fields = {
            'header_image': media_expandable_fields,
            'category': (
                BlogPostCategorySerializer,
                {'many': False, 'fields': [
                    'name',
                ]}
            ),
            'author': user_expandable_fields
        }


class BlogPostCategoryOverViewSerializer(FlexFieldsModelSerializer):
    last_posts = serializers.SerializerMethodField()

    def get_last_posts(self, obj: BlogCategory):
        serializer = BlogPostSerializer(obj.blogpost_set.all()[:10], many=True, expand=['author', 'header_image'],
                                        fields=['author', 'created_at', 'title', 'excerpt', 'header_image',
                                                'tags', 'slug', 'read_time'])
        return serializer.data

    class Meta:
        model = BlogCategory
        fields = ['name', 'order', 'is_active', 'last_posts','id']


"""
Frequently asked questions
"""


class FAQCategorySerializer(FlexFieldsModelSerializer):
    class Meta:
        model = FrequentlyAskedQuestionCategory
        fields = '__all__'


class FAQSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = FrequentlyAskedQuestion
        fields = '__all__'
        read_only_fields = ['created_by']
        expandable_fields = {
            'category': (
                FAQCategorySerializer,
                {'many': False, 'fields': [
                    'name',
                ]}
            ),
            'created_by': user_expandable_fields,
        }


class EventSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        expandable_fields = {
            'header_image': media_expandable_fields
        }
