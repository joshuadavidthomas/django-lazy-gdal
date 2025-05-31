"""
Lazy imports for Django's GDAL error module to avoid triggering GDAL loading.
"""

from __future__ import annotations

from django.utils.functional import SimpleLazyObject


def _get_gdal_exception():
    from django.contrib.gis.gdal.error import GDALException
    return GDALException


def _get_srs_exception():
    from django.contrib.gis.gdal.error import SRSException
    return SRSException


def _get_check_err():
    from django.contrib.gis.gdal.error import check_err
    return check_err


GDALException = SimpleLazyObject(_get_gdal_exception)
SRSException = SimpleLazyObject(_get_srs_exception)
check_err = SimpleLazyObject(_get_check_err)