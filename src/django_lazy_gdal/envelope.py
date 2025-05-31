"""
Lazy imports for Django's GDAL envelope module to avoid triggering GDAL loading.
"""

from __future__ import annotations

from django.utils.functional import SimpleLazyObject


def _get_ogr_envelope():
    from django.contrib.gis.gdal.envelope import OGREnvelope
    return OGREnvelope


def _get_envelope():
    from django.contrib.gis.gdal.envelope import Envelope
    return Envelope


OGREnvelope = SimpleLazyObject(_get_ogr_envelope)
Envelope = SimpleLazyObject(_get_envelope)