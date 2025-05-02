from __future__ import annotations

import importlib
import logging
import sys
from typing import Any

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
    lazy_libgdal_mod = "django_lazy_gdal.lazy_libgdal"

    original_libgdal = None
    original_module_dict: dict[str, Any] = {}
    try:
        if (
            django_libgdal_mod in sys.modules
            and sys.modules[django_libgdal_mod] is not lazy_libgdal
        ):
            logger.warning(
                f"{django_libgdal_mod} was imported before django_lazy_gdal could monkeypatch it. "
                "Call django_lazy_gdal.monkeypatch_libgdal() early in your settings module."
            )
            original_libgdal = sys.modules[django_libgdal_mod]
        elif django_libgdal_mod not in sys.modules:
            try:
                original_libgdal = importlib.import_module(django_libgdal_mod)
            except ImportError:
                # This might happen if django.contrib.gis is partially available
                # but libgdal itself fails to import. Patching might still be desired
                # but attribute copying won't work.
                logger.warning(
                    f"Could not import original {django_libgdal_mod} for attribute copying.",
                    exc_info=True,
                )
                pass

        if original_libgdal:
            original_module_dict = original_libgdal.__dict__.copy()

    except Exception:
        logger.exception(
            f"Error trying to access original module {django_libgdal_mod} for attribute copying."
        )
        # Decide whether to proceed without attribute copying or bail out.
        # Let's proceed but without attributes.
        pass

    sys.modules[django_libgdal_mod] = lazy_libgdal
    logger.debug(f"Monkeypatched {django_libgdal_mod} to use {lazy_libgdal_mod}")

    # Transfer attributes from the original module dict if we have it
    if original_module_dict:
        copied_attrs_count = 0
        for key, value in original_module_dict.items():
            # Only copy if the attribute doesn't already exist on the lazy module
            if not hasattr(lazy_libgdal, key):
                try:
                    setattr(lazy_libgdal, key, value)
                    copied_attrs_count += 1
                except Exception:
                    logger.warning(
                        f"Failed to copy attribute '{key}' from original {django_libgdal_mod} to lazy module.",
                        exc_info=True,
                    )
                    pass
        logger.debug(
            f"Transferred {copied_attrs_count} missing attributes from {django_libgdal_mod}."
        )
    else:
        logger.debug(
            f"Skipping attribute transfer as original module dict for {django_libgdal_mod} wasn't available."
        )
