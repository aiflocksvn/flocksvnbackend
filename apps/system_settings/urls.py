from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .api import SystemOptionPublicAPI

setting_router = SimpleRouter()
setting_router.register('', SystemOptionPublicAPI, basename='public_event')

urlpatterns = [
    path('', include(setting_router.urls))
]
