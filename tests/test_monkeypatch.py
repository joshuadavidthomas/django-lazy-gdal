from __future__ import annotations

import sys
from unittest import mock

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


def test_monkeypatch_doesnt_import_django_libgdal():
    """Test that monkeypatching doesn't trigger GDAL loading by importing Django's module."""
    import django_lazy_gdal

    # Mock the importlib.import_module function to detect any attempts to import Django's GDAL module
    with mock.patch("importlib.import_module") as mock_import:
        # Run the monkeypatch function
        django_lazy_gdal.monkeypatch()

        # Verify importlib.import_module wasn't called with Django's GDAL module
        for call in mock_import.call_args_list:
            args, _ = call
            if args and args[0] == "django.contrib.gis.gdal.libgdal":
                pytest.fail(
                    "Monkeypatching tried to import django.contrib.gis.gdal.libgdal"
                )

        # Alternative verification - look for any calls with GDAL or libgdal in the module name
        django_gdal_imports = [
            args[0]
            for args, _ in mock_import.call_args_list
            if args
            and "django" in args[0]
            and ("gdal" in args[0].lower() or "libgdal" in args[0].lower())
        ]
        assert not django_gdal_imports, (
            f"Monkeypatching imported Django GDAL modules: {django_gdal_imports}"
        )
