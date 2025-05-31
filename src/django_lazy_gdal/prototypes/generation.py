"""
This module contains functions that generate ctypes prototypes for the
GDAL routines.
"""

from __future__ import annotations

from ctypes import POINTER
from ctypes import c_bool
from ctypes import c_char_p
from ctypes import c_double
from ctypes import c_int
from ctypes import c_int64
from ctypes import c_void_p
from functools import partial

from django.contrib.gis.gdal.prototypes.errcheck import check_arg_errcode
from django.contrib.gis.gdal.prototypes.errcheck import check_const_string
from django.contrib.gis.gdal.prototypes.errcheck import check_errcode
from django.contrib.gis.gdal.prototypes.errcheck import check_geom
from django.contrib.gis.gdal.prototypes.errcheck import check_geom_offset
from django.contrib.gis.gdal.prototypes.errcheck import check_pointer
from django.contrib.gis.gdal.prototypes.errcheck import check_srs
from django.contrib.gis.gdal.prototypes.errcheck import check_str_arg
from django.contrib.gis.gdal.prototypes.errcheck import check_string

from django_lazy_gdal.libgdal import GDALFuncFactory


class gdal_char_p(c_char_p):
    pass


def bool_output(func, argtypes, errcheck=None):
    """Generate a ctypes function that returns a boolean value."""
    func.argtypes = argtypes
    func.restype = c_bool
    if errcheck:
        func.errcheck = errcheck
    return func


class BoolOutput(GDALFuncFactory):
    """For GDAL routines that return a boolean as int."""

    restype = c_int
    errcheck = staticmethod(lambda result, func, cargs: bool(result))


def double_output(func, argtypes, errcheck=False, strarg=False, cpl=False):
    "Generate a ctypes function that returns a double value."
    func.argtypes = argtypes
    func.restype = c_double
    if errcheck:
        func.errcheck = partial(check_arg_errcode, cpl=cpl)
    if strarg:
        func.errcheck = check_str_arg
    return func


class DoubleOutput(GDALFuncFactory):
    """For GDAL routines that return a double."""

    restype = c_double


def geom_output(func, argtypes, offset=None):
    """
    Generate a function that returns a Geometry either by reference
    or directly (if the return_geom keyword is set to True).
    """
    # Setting the argument types
    func.argtypes = argtypes

    if not offset:
        # When a geometry pointer is directly returned.
        func.restype = c_void_p
        func.errcheck = check_geom
    else:
        # Error code returned, geometry is returned by-reference.
        func.restype = c_int

        def geomerrcheck(result, func, cargs):
            return check_geom_offset(result, func, cargs, offset)

        func.errcheck = geomerrcheck

    return func


class GeomOutput(GDALFuncFactory):
    """For GDAL routines that return a geometry."""

    restype = c_void_p
    errcheck = staticmethod(check_geom)


def int_output(func, argtypes, errcheck=None):
    "Generate a ctypes function that returns an integer value."
    func.argtypes = argtypes
    func.restype = c_int
    if errcheck:
        func.errcheck = errcheck
    return func


class IntOutput(GDALFuncFactory):
    """For GDAL routines that return an integer."""

    restype = c_int


def int64_output(func, argtypes):
    "Generate a ctypes function that returns a 64-bit integer value."
    func.argtypes = argtypes
    func.restype = c_int64
    return func


class Int64Output(GDALFuncFactory):
    """For GDAL routines that return a 64-bit integer."""

    restype = c_long


def srs_output(func, argtypes):
    """
    Generate a ctypes prototype for the given function with
    the given C arguments that returns a pointer to an OGR
    Spatial Reference System.
    """
    func.argtypes = argtypes
    func.restype = c_void_p
    func.errcheck = check_srs
    return func


class SRSOutput(GDALFuncFactory):
    "For GDAL routines that return a SpatialReference."

    restype = c_void_p
    errcheck = staticmethod(check_srs)


def const_string_output(func, argtypes, offset=None, decoding=None, cpl=False):
    func.argtypes = argtypes
    if offset:
        func.restype = c_int
    else:
        func.restype = c_char_p

    def _check_const(result, func, cargs):
        res = check_const_string(result, func, cargs, offset=offset, cpl=cpl)
        if res and decoding:
            res = res.decode(decoding)
        return res

    func.errcheck = _check_const

    return func


class ConstStringOutput(GDALFuncFactory):
    """For GDAL routines that return a const string."""

    restype = c_char_p
    errcheck = staticmethod(check_const_string)


def string_output(func, argtypes, offset=-1, str_result=False, decoding=None):
    """
    Generate a ctypes prototype for the given function with the
    given argument types that returns a string from a GDAL pointer.
    The `const` flag indicates whether the allocated pointer should
    be freed via the GDAL library routine VSIFree -- but only applies
    only when `str_result` is True.
    """
    func.argtypes = argtypes
    if str_result:
        # Use subclass of c_char_p so the error checking routine
        # can free the memory at the pointer's address.
        func.restype = gdal_char_p
    else:
        # Error code is returned
        func.restype = c_int

    # Dynamically defining our error-checking function with the
    # given offset.
    def _check_str(result, func, cargs):
        res = check_string(result, func, cargs, offset=offset, str_result=str_result)
        if res and decoding:
            res = res.decode(decoding)
        return res

    func.errcheck = _check_str
    return func


def void_output(func, argtypes, errcheck=True, cpl=False):
    """
    For functions that don't only return an error code that needs to
    be examined.
    """
    if argtypes:
        func.argtypes = argtypes
    if errcheck:
        # `errcheck` keyword may be set to False for routines that
        # return void, rather than a status code.
        func.restype = c_int
        func.errcheck = partial(check_errcode, cpl=cpl)
    else:
        func.restype = None

    return func


class VoidOutput(GDALFuncFactory):
    """For GDAL routines that return void."""

    def __init__(self, func_name, *, errcheck=True, cpl=False, **kwargs):
        super().__init__(func_name, **kwargs)
        if errcheck:
            # When errcheck=True, function returns int error code
            self.restype = c_int
            from functools import partial

            self.errcheck = staticmethod(partial(check_errcode, cpl=cpl))
        else:
            # When errcheck=False, function returns void
            self.restype = None
            self.errcheck = None


def voidptr_output(func, argtypes, errcheck=True):
    "For functions that return c_void_p."
    func.argtypes = argtypes
    func.restype = c_void_p
    if errcheck:
        func.errcheck = check_pointer
    return func


class VoidPtrOutput(GDALFuncFactory):
    """For GDAL routines that return void pointers."""

    restype = c_void_p

    def __init__(self, func_name, *, errcheck=True, **kwargs):
        super().__init__(func_name, **kwargs)
        if errcheck:
            self.errcheck = staticmethod(check_pointer)
        else:
            self.errcheck = None


def chararray_output(func, argtypes, errcheck=True):
    """For functions that return a c_char_p array."""
    func.argtypes = argtypes
    func.restype = POINTER(c_char_p)
    if errcheck:
        func.errcheck = check_pointer
    return func
