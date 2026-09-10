import os
import secrets

# No sessions/signatures/persistent state: a process-local key suffices for this fixture.
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY") or secrets.token_hex(32)
DEBUG = False
# Stateless public fixture: accept the public host assigned at launch.
ALLOWED_HOSTS = os.getenv("APP_ALLOWED_HOSTS", "*").split(",")
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
INSTALLED_APPS = ["rest_framework"]
MIDDLEWARE = []
DATABASES = {}
APPEND_SLASH = False
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 4 * 1024 * 1024
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "UNAUTHENTICATED_USER": None,
}
