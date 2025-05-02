from __future__ import annotations

import sys
from importlib import import_module

import django
import pytest
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import SimpleLazyObject
from django.utils.functional import empty


def test_libgdal_is_monkeypatched():
    django.setup()

    from django_lazy_gdal import lazy_libgdal

    assert sys.modules["django.contrib.gis.gdal.libgdal"] is lazy_libgdal


@pytest.mark.parametrize(
    "INSTALLED_APPS",
    [
        [
            "django.contrib.gis",
        ],
        [
            "django_lazy_gdal",
            "django.contrib.gis",
        ],
    ],
)
def test_libgdal_is_normal(INSTALLED_APPS, settings):
    # test if the library is installed but not configured correctly
    # then libgdal is not monkeypatched

    settings.INSTALLED_APPS = INSTALLED_APPS

    target_module_name = "django.contrib.gis.gdal.libgdal"
    original_module = sys.modules.get(target_module_name)

    try:
        if target_module_name in sys.modules:
            del sys.modules[target_module_name]

        django.setup()

        try:
            django_libgdal = import_module(target_module_name)
        except ImproperlyConfigured:
            django_libgdal = None

        from django_lazy_gdal import lazy_libgdal

        assert django_libgdal is not lazy_libgdal

        if django_libgdal:
            assert sys.modules[target_module_name] is not lazy_libgdal
            assert django_libgdal.__name__ == target_module_name

    finally:
        if original_module:
            sys.modules[target_module_name] = original_module
        elif target_module_name in sys.modules:
            del sys.modules[target_module_name]


def test_lgdal_is_lazy():
    django.setup()

    from django.contrib.gis.gdal.libgdal import lgdal

    assert isinstance(lgdal, SimpleLazyObject)
    assert hasattr(lgdal, "_wrapped")
    assert lgdal._wrapped is empty
