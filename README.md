# django-lazy-gdal

[![PyPI](https://img.shields.io/pypi/v/django-lazy-gdal)](https://pypi.org/project/llm-uv-tool/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-lazy-gdal)
![Django Version](https://img.shields.io/badge/django-4.2%20%7C%205.1%20%7C%205.2%20%7C%20main-%2344B78B?labelColor=%23092E20)

A Django app that patches `django.contrib.gis` to lazily load the GDAL library, functioning as a drop-in replacement that follows the same pattern used for the GEOS library.

## Requirements

- Python 3.9, 3.10, 3.11, 3.12, 3.13
- Django 4.2, 5.1, 5.2

## Installation

1. Install the package from PyPI:

    ```bash
    python -m pip install django-lazy-gdal

    # or if you like the new hotness

    uv add django-lazy-gdal
    uv sync
    ```

2. Add the app to your Django project's `INSTALLED_APPS` **after** `django.contrib.gis`:

   ```python
   INSTALLED_APPS = [
       # Add these at the top 
       'django.contrib.gis',
       'django_lazy_gdal',
       # ...
   ]
   ```

> [!NOTE]
> **Order matters!** It's crucial to place `'django_lazy_gdal'` immediately after `'django.contrib.gis'` and before any other apps that might access the GeoDjango models in `django.contrib.gis.models` or access `django.contrib.gis.gdal.libgdal` directly. This ensures that the patching occurs before other apps access the module, making the lazy loading effective throughout your project.

3. That's it! The library will automatically patch Django's `django.contrib.gis.gdal.libgdal` module to use lazy loading.

## Why?

By default, Django's `django.contrib.gis.gdal.libgdal` module loads the GDAL library immediately upon import, which can cause issues if GDAL isn't installed. In contrast, the GEOS library in `django.contrib.gis.geos.libgeos` is lazily loaded using `SimpleLazyObject`, meaning errors are deferred until GEOS is actually used.

This provides several benefits:

- Enables calling `django.setup()` in projects using `django.contrib.gis` without requiring GDAL installation, allowing for runtime interaction with non-GIS parts of the project
- Prevents immediate import errors when GDAL isn't available, deferring them until actual GDAL use
- Potentially reduces initial overhead by delaying GDAL library loading

This project originated from the need to work with GeoDjango projects without requiring GDAL to be installed locally. While developing [django-language-server](https://github.com/joshuadavidthomas/django-language-server), I needed to set up Django to access information such as the template tags of the apps in `INSTALLED_APPS`.

However, I encountered errors when testing the language server on a project that uses GeoDjango but relies on Docker containers for development, thus bypassing the need to install Geospatial libraries locally.

This library uses monkeypatching as a temporary solution to modify Django's behavior regarding GDAL loading. The goal is to test the viability of lazily loading GDAL before proposing these changes upstream to Django. Hopefully, in the future, this library can be deprecated if/when this functionality is integrated into Django itself.

## License

django-lazy-gdal is licensed under the MIT license. See the [`LICENSE`](LICENSE) file for more information.
