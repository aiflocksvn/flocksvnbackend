from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.learning_board.models import BlogPost, BlogCategory, FrequentlyAskedQuestionCategory, FrequentlyAskedQuestion, \
    Event
from apps.learning_board.serialziers import BlogPostSerializer, BlogPostCategorySerializer, \
    BlogPostCategoryOverViewSerializer, FAQCategorySerializer, FAQSerializer, EventSerializer
from utils.views import FilterMixin


class BlogPostPublicAPI(FilterMixin, ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    filter_fields = ['author__id', 'created_at', 'category__id', 'post_status', 'comment_status']
    search_fields = ['title', 'excerpt', 'raw_content']
    ordering_fields = ['author', 'created_at', 'modified_at', 'post_status', 'comment_status']
    lookup_field = 'slug'

    def get_queryset(self):
        return self.queryset.filter(post_status=BlogPost.PUBLISH)

    @action(detail=True, methods=['GET'])
    def related(self, request, slug):
        instance: BlogPost = self.get_object()
        queryset = self.get_queryset().filter(category_id=instance.category_id).exclude(slug=slug)[:3]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# TODO filter active blog post
class BlogPostCategoryPublicAPI(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = BlogCategory.objects.all()
    serializer_class = BlogPostCategorySerializer
    filter_fields = ['name']
    search_fields = filter_fields
    ordering_fields = filter_fields

    def get_queryset(self):
        return self.queryset.filter(is_active=True).order_by('order')

    @action(detail=True, methods=['GET'], serializer_class=BlogPostSerializer)
    def post(self, request, pk):
        queryset = self.get_object().blogpost_set.filter(post_status=BlogPost.PUBLISH)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'], serializer_class=BlogPostCategoryOverViewSerializer)
    def overview_with_post(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class FAQCategoryPublicApi(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = FrequentlyAskedQuestionCategory.objects.all()
    serializer_class = FAQCategorySerializer
    filter_fields = ['name']
    search_fields = filter_fields
    ordering_fields = filter_fields

    @action(detail=True, methods=['GET'], serializer_class=FAQSerializer)
    def questions(self, request, pk):
        queryset: FrequentlyAskedQuestionCategory = self.get_object().frequentlyaskedquestion_set.filter(is_active=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class FAQPublicApi(FilterMixin,ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = FrequentlyAskedQuestion.objects.all()
    serializer_class = FAQSerializer
    filter_fields = ['title', 'raw_content']
    search_fields = filter_fields
    ordering_fields = filter_fields


class EventPublicApi(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_fields = []
    search_fields = filter_fields
    ordering_fields = filter_fields
