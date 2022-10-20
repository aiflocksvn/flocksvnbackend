from django.utils.translation import gettext_lazy as _

from .common import *

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGES = [
    ('vi', _('Vietnam')),
    ('en', _('English')),
]
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True
LOCALE_PATHS = [
    BASE_DIR / 'localization/',
]
MIDDLEWARE += [
    'django.middleware.locale.LocaleMiddleware'
]
