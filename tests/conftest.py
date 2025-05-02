from __future__ import annotations

import logging

from django.conf import settings

from .settings import TEST_SETTINGS

pytest_plugins = []


def pytest_configure(config) -> None:
    logging.disable(logging.CRITICAL)

    settings.configure(**TEST_SETTINGS)
