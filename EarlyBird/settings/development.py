# ##### DEBUG CONFIGURATION ###############################
from datetime import timedelta

from corsheaders.defaults import default_headers, default_methods

from .i18n import *

SECRET_KEY = '3=92xbzk^y@a*ve27oc!(l_jrlu$hikpf!w75s@h_4-nua!02v'
EXTRA_SECRET_KEY = 'v72m=(#0dhvw_a=21+cd)#n+u_roc@vn2#@@#if5jxn3%t^%%^'

DEBUG = True
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = list(default_headers) + [
    "api-key"
]
CORS_ALLOW_METHODS = ("DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT")
# allow all hosts during development
ALLOWED_HOSTS = ['*']
INSTALLED_APPS += [
    'drf_spectacular',
    "django_advance_dumpdata",
    'flocks-admin-dashboard-gules.vercel.app',
    'flocks-website.vercel.app',
    'api.flocks.vn',
    'uploads.flocks.vn',
]

# ##### DATABASE CONFIGURATION ############################
DATABASES = {
    'default': {

        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'earlybird',
        'USER': 'postgres',
        'PASSWORD': 'safirco',
        'HOST': 'localhost',
        'ATOMIC_REQUEST': True,
        'PORT': 5432,
    }
}

# ##### APPLICATION CONFIGURATION #########################

SPECTACULAR_SETTINGS = {
    'TITLE': 'EarlyBird Api',
    'DESCRIPTION': 'CrowdFounding System',
    'VERSION': '1.0.0',
    'SCHEMA_PATH_PREFIX': r'/api/v[0-9]',
}
# INSTALLED_APPS = DEFAULT_APPS
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}

"""
Media Setting
"""

IMG_MAX_UPLOAD_SIZE = 5
VIDEO_MAX_UPLOAD_SIZE = 100
DOCS_MAX_UPLOAD_SIZE = 5
VALID_IMAGE = [
    'image/avif',
    'image/bmp',
    'image/gif',
    'image/jpeg',
    'image/jpg',
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
BACKUP_ROOT = join(BASE_DIR, 'run', 'backups_files')
SECURE_MEDIA = join(BASE_DIR, 'run', 'secure_media')

"""
SIMPLE_JWT
"""

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=100),
    'UPDATE_LAST_LOGIN': True,
    # 'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
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
SESSION_COOKIE_AGE = 1209600 / 2  # 1 Weeks

"""
WEBSITE SETTING
"""
## website
FRONT_MAIN_BASE_URL = 'http://localhost:3000'
FRONT_MAIN_CONFIRM_EMAIL_URL = f'{FRONT_MAIN_BASE_URL}/verify/?token=%s'
FRONT_MAIN_CONFIRM_RESET_PASSWORD_URL = f'{FRONT_MAIN_BASE_URL}/confirm_reset_password/?token=%s'
WEBSITE_NAME = 'Flocks AI'
WEBSITE_MAIN_URL = FRONT_MAIN_BASE_URL

## landing page
FRONT_LANDING_PAGE_BASE_URL = 'http://localhost200:3000'
FRONT_LANDING_PAGE_CONFIRM_EMAIL_URL = f'{FRONT_LANDING_PAGE_BASE_URL}/verify/?token=%s'
FRONT_LANDING_PAGE_CONFIRM_RESET_PASSWORD_URL = f'{FRONT_LANDING_PAGE_BASE_URL}/confirm_reset_password/?token=%s'
WEBSITE_LANDING_PAGE_URL = FRONT_LANDING_PAGE_BASE_URL

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# sentry_sdk.init(
#     dsn="https://9772db71d0764383b60acbc5e42a4e87@o1172601.ingest.sentry.io/6267547",
#     integrations=[DjangoIntegration()],
#
#     # Set traces_sample_rate to 1.0 to capture 100%
#     # of transactions for performance monitoring.
#     # We recommend adjusting this value in production.
#     traces_sample_rate=1.0,
#     environment="development",
#
#     # If you wish to associate users to errors (assuming you are using
#     # django.contrib.auth) you may enable sending PII data.
#     send_default_pii=True
# )
# EMAIL_BACKEND = 'django_smtp_ssl.SSLEmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'shadow.mxrouting.net'
# EMAIL_PORT = 25
# EMAIL_USE_TLS = True
# EMAIL_USE_SSL = False
# EMAIL_HOST_USER = 'info@flocks.vn'
# EMAIL_HOST_PASSWORD = 'LETmein01'
