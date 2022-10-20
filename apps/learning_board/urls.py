from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .api import BlogPostPublicAPI, BlogPostCategoryPublicAPI, FAQPublicApi, FAQCategoryPublicApi, EventPublicApi

learning_board_router = SimpleRouter()
learning_board_router.register('blog/category', BlogPostCategoryPublicAPI, basename='public_blog_category')
learning_board_router.register('blog', BlogPostPublicAPI, basename='public_blog')
learning_board_router.register('faq/category', FAQCategoryPublicApi, basename='public_faq_category')
learning_board_router.register('faq', FAQPublicApi, basename='public_faq')
learning_board_router.register('event', EventPublicApi, basename='public_event')

urlpatterns = [
    path('', include(learning_board_router.urls)),

]
