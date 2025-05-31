from __future__ import annotations

import logging
import sys

logger = logging.getLogger(__name__)

_patching_done = False


def monkeypatch() -> None:
    """
    Monkeypatches Django's GDAL library loader to use our lazy loader instead.

    This function must be called before Django's model importing phase to be effective.
    Typically, it should be called at the top of your settings module, before any
    apps or models are imported.
    """
    global _patching_done

    if _patching_done:
        logger.debug("Patching already attempted. Skipping.")
        return
    _patching_done = True

    from django_lazy_gdal import libgdal as lazy_libgdal

    django_libgdal_mod = "django.contrib.gis.gdal.libgdal"
    lazy_libgdal_mod = "django_lazy_gdal.libgdal"

    if (
        django_libgdal_mod in sys.modules
        and sys.modules[django_libgdal_mod] is not lazy_libgdal
    ):
        logger.warning(
            f"{django_libgdal_mod} was imported before django_lazy_gdal could monkeypatch it. Call django_lazy_gdal.monkeypatch() early in your settings module."
        )

    sys.modules[django_libgdal_mod] = lazy_libgdal
    logger.debug(f"Monkeypatched {django_libgdal_mod} to use {lazy_libgdal_mod}")

    # Monkeypatch prototypes modules (excluding generation which we renamed)
    prototype_modules = ["ds", "geom", "raster", "srs"]
    for module_name in prototype_modules:
        django_mod = f"django.contrib.gis.gdal.prototypes.{module_name}"
        lazy_mod = f"django_lazy_gdal.prototypes.{module_name}"

        # Import our lazy module
        lazy_module = __import__(lazy_mod, fromlist=[module_name])

        if django_mod in sys.modules and sys.modules[django_mod] is not lazy_module:
            logger.warning(
                f"{django_mod} was imported before django_lazy_gdal could monkeypatch it."
            )

        sys.modules[django_mod] = lazy_module
        logger.debug(f"Monkeypatched {django_mod} to use {lazy_mod}")
