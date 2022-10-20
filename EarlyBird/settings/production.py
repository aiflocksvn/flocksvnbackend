# for now fetch the development settings only
# turn off all debugging
import os
from datetime import timedelta

from corsheaders.defaults import default_headers, default_methods

from .i18n import *

DEBUG = False
ALLOWED_HOSTS = [
    'www.anarsupermarket.website',
    'anarsupermarket.website',
    'flocks.vn',
    'flocks-admin-dashboard-gules.vercel.app',
    'flocksvn-frnj.vercel.app',
    'flocks-website.vercel.app',
    '127.0.0.1',
    'api.flocks.vn',
    'uploads.flocks.vn',
    '54.203.235.172'
]

CORS_ALLOWED_ORIGINS = [
     "https://flocks.vn",
     "https://www.flocks.vn",
     "http://localhost:3000",
     "https://localhost:3000",
     "https://flocks-admin-dashboard-gules.vercel.app",
     "https://flocks-admin-dashboard-e92ennyjj-dashboardflocks.vercel.app",
     "https://www.dashboard.flocks.vn",
     "https://flocks-website.vercel.app",
     "https://flocksvn-frnj.vercel.app"
 ]

CORS_ALLOW_HEADERS = list(default_headers) + [
    "api-key"
]
CORS_ALLOW_METHODS = list(default_methods)
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

SECRET_KEY = os.environ['SECRET_KEY']
EXTRA_SECRET_KEY = os.environ['EXTRA_SECRET_KEY']

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.environ['PSQL_ENGINE'],
        'NAME': os.environ['PSQL_DATABASE'],
        'USER': os.environ['PSQL_USER'],
        'PASSWORD': os.environ['PSQL_PASSWORD'],
        'HOST': os.environ['PSQL_HOST'],
        'PORT': os.environ['PSQL_PORT'],
        "atomic_request": True
    }
}
# ##### SECURITY CONFIGURATION ############################


# redirects all requests to https
# SESSION_COOKIE_SECURE = False
SESSION_COOKIE_AGE = 1209600
SESSION_COOKIE_HTTPONLY = True

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# the email address, these error notifications to admins come from
SERVER_EMAIL = 'ehsan.safir@microcis.net'

# how many days a password reset should work. I'd say even one day is too long
# PASSWORD_RESET_TIMEOUT_DAYS = 1
CSRF_TRUSTED_ORIGINS = ['https://*.anarsupermarket.website']

"""
Media Setting
"""

IMG_MAX_UPLOAD_SIZE = 5
VIDEO_MAX_UPLOAD_SIZE = 50
DOCS_MAX_UPLOAD_SIZE = 20
VALID_IMAGE = [
    'image/avif',
    'image/bmp',
    'image/gif',
    'image/jpeg',
    'image/png',
    'image/webp'
]
VALID_VIDEO = [
    'video/mp4',
    'video/mpeg',
    'video/ogg',
    'video/webm',
    "video/3gpp; audio/3gpp if it doesn't contain video",
    "video/3gpp2; audio/3gpp2 if it doesn't contain video"
]
VALID_DOCS = [
    'application/x-abiword',
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/msword',
    'application/rtf',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-excel',
    'application/vnd.oasis.opendocument.spreadsheet',
]
VALID_CONTENT_TYPE = VALID_IMAGE + VALID_VIDEO + VALID_DOCS

MEDIA_URL = '/media/'
MEDIA_ROOT = join(BASE_DIR, 'run', 'media')
SECURE_MEDIA = join(BASE_DIR, 'run', 'secure_media')
"""
SIMPLE_JWT
"""

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=15),
    'UPDATE_LAST_LOGIN': True,
}

"""
RestFrameWork
"""

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': (
        'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        # 'djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer',
        # Any other renders
    ),

    'DEFAULT_PARSER_CLASSES': (
        # If you use MultiPartFormParser or FormParser, we also have a camel case version
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
        # Any other parsers
    ),

    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'utils.pagination.Paginator',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}
"""
Custom Token Setting
"""

TOKEN_EMAIL_VARIFY_EXPIRE = {"days": 1}
TOKEN_EMAIL_RESET_PASSWORD_EXPIRE = {"days": 1}
TOKEN_PHONE_RESET_PASSWORD_EXPIRE = {"days": 1}
TOKEN_OAUTH_STATE_EXPIRE = {"minutes": 20}

"""
Session 
"""
SESSION_COOKIE_AGE = 1209600  # 2 Weeks

"""
Front End Setting
"""

# """
# Landing page
# """
# FRONT_MAIN_BASE_URL = 'https://flocks.vn'
# FRONT_MAIN_CONFIRM_EMAIL_URL = f'{FRONT_MAIN_BASE_URL}/verify/?token=%s'
# FRONT_MAIN_CONFIRM_RESET_PASSWORD_URL = f'{FRONT_MAIN_BASE_URL}/confirm_reset_password/?token=%s'
# WEBSITE_NAME = 'Flocks AI'
# WEBSITE_MAIN_URL = FRONT_MAIN_BASE_URL
"""
WEBSITE SETTING
"""
## website
FRONT_MAIN_BASE_URL = 'https://flocks-website.vercel.app'
FRONT_MAIN_CONFIRM_EMAIL_URL = f'{FRONT_MAIN_BASE_URL}/verify/?token=%s'
FRONT_MAIN_CONFIRM_RESET_PASSWORD_URL = f'{FRONT_MAIN_BASE_URL}/confirm_reset_password/?token=%s'
WEBSITE_NAME = 'Flocks AI'
WEBSITE_MAIN_URL = FRONT_MAIN_BASE_URL

## landing page
FRONT_LANDING_PAGE_BASE_URL = 'https://flocks.vn'
FRONT_LANDING_PAGE_CONFIRM_EMAIL_URL = f'{FRONT_LANDING_PAGE_BASE_URL}/verify/?token=%s'
FRONT_LANDING_PAGE_CONFIRM_RESET_PASSWORD_URL = f'{FRONT_LANDING_PAGE_BASE_URL}/confirm_reset_password/?token=%s'
WEBSITE_LANDING_PAGE_URL = FRONT_LANDING_PAGE_BASE_URL

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://9772db71d0764383b60acbc5e42a4e87@o1172601.ingest.sentry.io/6267547",
    integrations=[DjangoIntegration()],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,
    environment="production",

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)
