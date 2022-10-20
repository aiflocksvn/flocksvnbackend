import os

from .development import *

# REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = []
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = ('rest_framework.renderers.JSONRenderer',)
# REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = []

USE_TZ = False
TIME_ZONE = 'UTC'
INITIAL_TEST_FIXTURES_PATH = 'run/fixtures/test_data'

FIXTURE_DIRS = (
    os.path.join(BASE_DIR, 'run/fixtures/test_data/'),
)
