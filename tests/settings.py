from __future__ import annotations

TEST_SETTINGS = {
    "ALLOWED_HOSTS": ["*"],
    "DEBUG": False,
    "CACHES": {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    },
    "DATABASES": {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    },
    "EMAIL_BACKEND": "django.core.mail.backends.locmem.EmailBackend",
    "INSTALLED_APPS": [
        "django.contrib.gis",
        "django_lazy_gdal",
    ],
    "LOGGING_CONFIG": None,
    "PASSWORD_HASHERS": [
        "django.contrib.auth.hashers.MD5PasswordHasher",
    ],
    "SECRET_KEY": "not-a-secret",
}
