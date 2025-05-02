from __future__ import annotations

import sys

import pytest
from django.utils.functional import SimpleLazyObject
from django.utils.functional import empty


@pytest.fixture(autouse=True)
def setup():
    # Reset patching flag
    import django_lazy_gdal

    django_lazy_gdal._patching_done = False

    target_module_name = "django.contrib.gis.gdal.libgdal"
    original_module = sys.modules.get(target_module_name)

    try:
        if target_module_name in sys.modules:
            del sys.modules[target_module_name]

        if "django_lazy_gdal.libgdal" in sys.modules:
            del sys.modules["django_lazy_gdal.libgdal"]

        yield

    finally:
        if original_module:
            sys.modules[target_module_name] = original_module
        elif target_module_name in sys.modules:
            del sys.modules[target_module_name]


def test_monkeypatch_libgdal():
    import django_lazy_gdal

    django_lazy_gdal.monkeypatch()

    from django_lazy_gdal import libgdal as lazy_libgdal

    assert sys.modules["django.contrib.gis.gdal.libgdal"] is lazy_libgdal


def test_monkeypatch_only_once():
    import django_lazy_gdal

    django_lazy_gdal.monkeypatch()
    assert django_lazy_gdal._patching_done is True

    current_module = sys.modules["django.contrib.gis.gdal.libgdal"]

    mock_module = object()
    sys.modules["django.contrib.gis.gdal.libgdal"] = mock_module

    # should be a no-op
    django_lazy_gdal.monkeypatch()

    assert sys.modules["django.contrib.gis.gdal.libgdal"] is mock_module

    sys.modules["django.contrib.gis.gdal.libgdal"] = current_module


def test_lgdal_is_lazy_after_monkeypatch():
    import django_lazy_gdal

    django_lazy_gdal.monkeypatch()

    from django.contrib.gis.gdal.libgdal import lgdal

    assert isinstance(lgdal, SimpleLazyObject)
    assert hasattr(lgdal, "_wrapped")
    assert lgdal._wrapped is empty
