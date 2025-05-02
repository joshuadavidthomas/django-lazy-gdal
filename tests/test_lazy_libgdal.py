from __future__ import annotations

import os
import sys
from unittest import mock

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import SimpleLazyObject
from django.utils.functional import empty

# Testing for the lazy loading of the GDAL library - whether or not GDAL
# is installed - verifying that:
#
# - The GDAL library is not loaded upon importing `django_lazy_gdal.libgdal`.
# - The library is loaded only once upon the first access to an attribute
#   of the lazy object.
# - Subsequent accesses do not reload the library.
# - The lazy objects use the `empty` sentinel from `django.utils.functional`
#   to indicate whether the loading function has been called.
# - Appropriate exceptions are raised when the GDAL library cannot be found.
#
# The tests avoid dependency on the actual GDAL library by handling
# `AttributeError` from accessing non-existent attributes and by mocking
# where necessary.


@pytest.fixture(autouse=True)
def setup():
    # Clean up modules before each test
    modules_to_clean = [
        "django_lazy_gdal.libgdal",
        "django.contrib.gis.gdal.libgdal",
    ]
    for module in modules_to_clean:
        if module in sys.modules:
            del sys.modules[module]
    yield
    # Clean up after test
    for module in modules_to_clean:
        if module in sys.modules:
            del sys.modules[module]


def test_lgdal_not_loaded_on_import():
    import django_lazy_gdal.libgdal as lazy_libgdal

    assert isinstance(lazy_libgdal.lgdal, SimpleLazyObject)
    assert hasattr(lazy_libgdal.lgdal, "_wrapped")
    assert lazy_libgdal.lgdal._wrapped is empty


@pytest.mark.skipif(os.name != "nt", reason="lwingdal is Windows-specific")
def test_lwingdal_not_loaded_on_import():
    import django_lazy_gdal.libgdal as lazy_libgdal

    assert isinstance(lazy_libgdal.lwingdal, SimpleLazyObject)
    assert hasattr(lazy_libgdal.lwingdal, "_wrapped")
    assert lazy_libgdal.lwingdal._wrapped is empty


def test_lgdal_loaded_on_first_access():
    import django_lazy_gdal.libgdal as lazy_libgdal

    assert lazy_libgdal.lgdal._wrapped is empty

    try:
        with pytest.raises(AttributeError):
            lazy_libgdal.lgdal.some_attribute

        assert lazy_libgdal.lgdal._wrapped is not empty
    except ImproperlyConfigured:
        # GDAL is not installed, but our wrapper worked
        pass


@pytest.mark.skipif(os.name != "nt", reason="lwingdal is Windows-specific")
def test_lwingdal_loaded_on_first_access():
    import django_lazy_gdal.libgdal as lazy_libgdal

    assert lazy_libgdal.lwingdal._wrapped is empty

    try:
        with pytest.raises(AttributeError):
            lazy_libgdal.lwingdal.some_attribute

        assert lazy_libgdal.lwingdal._wrapped is not empty
    except ImproperlyConfigured:
        # GDAL is not installed, but our wrapper worked
        pass


def test_lgdal_load_is_cached():
    import django_lazy_gdal.libgdal as lazy_libgdal

    assert lazy_libgdal.lgdal._wrapped is empty

    try:
        with pytest.raises(AttributeError):
            lazy_libgdal.lgdal.some_attribute

        first_loaded_object = lazy_libgdal.lgdal._wrapped
        assert first_loaded_object is not empty

        with pytest.raises(AttributeError):
            lazy_libgdal.lgdal.another_attribute

        second_loaded_object = lazy_libgdal.lgdal._wrapped
        assert second_loaded_object is not empty
        assert second_loaded_object is first_loaded_object
    except ImproperlyConfigured:
        # GDAL is not installed, but our wrapper worked
        pass


@pytest.mark.skipif(os.name != "nt", reason="lwingdal is Windows-specific")
def test_lwingdal_load_is_cached():
    import django_lazy_gdal.libgdal as lazy_libgdal

    assert lazy_libgdal.lwingdal._wrapped is empty

    try:
        with pytest.raises(AttributeError):
            lazy_libgdal.lwingdal.some_attribute

        first_loaded_object = lazy_libgdal.lwingdal._wrapped
        assert first_loaded_object is not empty

        with pytest.raises(AttributeError):
            lazy_libgdal.lwingdal.another_attribute

        second_loaded_object = lazy_libgdal.lwingdal._wrapped
        assert second_loaded_object is not empty
        assert second_loaded_object is first_loaded_object
    except ImproperlyConfigured:
        # GDAL is not installed, but our wrapper worked
        pass


@mock.patch("ctypes.util.find_library")
def test_load_gdal_failure(mock_find_library):
    mock_find_library.return_value = None

    import django_lazy_gdal.libgdal as lazy_libgdal

    with pytest.raises(ImproperlyConfigured, match="Could not find the GDAL library"):
        lazy_libgdal.lgdal.some_attribute
