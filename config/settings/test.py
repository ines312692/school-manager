from .base import *

DEBUG = False

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

STORAGES = {
    **STORAGES,
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}

LOGGING = {
    **LOGGING,
    "root": {"handlers": ["console"], "level": "WARNING"},
    "loggers": {
        **LOGGING["loggers"],
        "django.request": {"level": "CRITICAL", "propagate": True},
    },
}

WHITENOISE_AUTOREFRESH = True
