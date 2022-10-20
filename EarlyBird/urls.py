"""EarlyBird URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import random

from django.conf import settings

from django.contrib import admin
from django.shortcuts import render
from django.urls import path, include
from rest_framework import status
from rest_framework.response import Response


def test(request):
    error_code = random.randint(500, 511)

    return render(request, 'firebase_auth.html', status=error_code)


BASE_URL = 'api/v1/'
urlpatterns = [

    path(BASE_URL + 'company/', include('apps.company.urls')),
    path(BASE_URL + 'investment/', include('apps.investment.urls')),
    path(BASE_URL + 'auth/', include('apps.authentication.urls')),
    path(BASE_URL + 'setting/', include('apps.system_settings.urls')),
    path(BASE_URL + 'media/', include('apps.media_center.urls')),
    path(BASE_URL + 'setting/', include('apps.system_settings.urls')),
    path(BASE_URL + 'payment/', include('apps.payment.urls')),
    path(BASE_URL + 'challenge/', include('apps.challenge.urls')),
    path(BASE_URL, include('apps.dashboard.urls')),
    path(BASE_URL, include('apps.learning_board.urls')),
    path(BASE_URL + 'test/', test),

]

if settings.DEBUG:
    from django.conf.urls.static import static
    from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static('backups_file/', document_root=settings.BACKUP_ROOT)
    urlpatterns += [
        path('admin/', admin.site.urls),
        path(BASE_URL + 'schema/', SpectacularAPIView.as_view(), name='schema'),
        path(BASE_URL + 'docs/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path(BASE_URL + 'docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]
