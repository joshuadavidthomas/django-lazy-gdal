from __future__ import annotations

from typing import final

from django.apps import AppConfig


@final
class DjangoLazyGDALConfig(AppConfig):
    name = "django_lazy_gdal"
    verbose_name = "Django Lazy GDAL"
