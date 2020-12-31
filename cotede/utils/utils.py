# -*- coding: utf-8 -*-

"""Utilities for CoTeDe

Miscelaneous resources to support CoTeDe.
"""

import json
import logging
import numpy as np
import os
from os.path import expanduser
import re
import pkg_resources

module_logger = logging.getLogger(__name__)


def cotederc(subdir=None):
    """Directory with custom configuration for CoTeDe

    To keep the local environment tight, CoTeDe expects to find all local files,
    like pre-set QC procedures, in one single place. This function returns the
    path to that directory.

    Parameters
    ----------
    subdir : str, optional
        Sub-directory inside the base custom directory.

    Returns
    -------
    str
        A path to the local custom files.

        The default path is a directory at the user's home like::

            ~/.config/cotederc/

    Note
    ----
    That default path can be modified by defining the environment variable
    COTEDE_DIR. On bash that could be done like::

        export COTEDE_DIR='/my/other/awesome/path/'

    Note
    ----
    For windows users the path is automatically adjusted to reflect its
    syntax.

    Example
    -------
    A sub-directory for configuration files, named 'cfg', can be determined by::

    >>> cotederc('cfg')
    """
    path = os.getenv("COTEDE_DIR", os.path.join("~", ".config", "cotederc"))
    path = os.path.expanduser(path)
    if subdir is not None:
        path = os.path.join(path, subdir)
    return path


def _coordinate_flex_vocabulary(obj, latname=None, lonname=None):
    """Extract the coordinates from the input object

    The coordinates latitude and longitude can have different names according
    to the vocabulary used. This function will try a sequence of possibilities
    and return the first one it finds.

    If custom names are given, those are the only ones considered. Otherwise,
    search for latitude and longitude coordinates in the following order:
    - LATITUDE/LONGITUDE
    - latitude/longitude
    - LAT/LON
    - lat/lon

    Parameters
    ----------
    obj :
        Input object. Typically a dictionary, pandas.DataFrame, or
        xarray.Dataset

    Returns
    -------
    lat : int, array_like
        Latitude coordinate(s)
    lon : int, array_like
        Longitude coordinate(s)

    Notes
    -----
    - If latname or lonname is defined, the other must be defiined as well. Both coordinates
      should be consistent, thus if the user will overwrite the most common vocabularies, it
      should be consistent between lat and lon.
    """
    if (latname is not None) or (lonname is not None):
        try:
            lat = obj[latname]
            lon = obj[lonname]
        except KeyError:
            raise LookupError

        if (np.size(lat) > 1) and (np.size(lon) > 1):
            lat = np.atleast_1d(lat)
            lon = np.atleast_1d(lon)
        return lat, lon

    vocab = [
        {"lat": "LATITUDE", "lon": "LONGITUDE"},
        {"lat": "latitude", "lon": "longitude"},
        {"lat": "lat", "lon": "lon"},
        {"lat": "LAT", "lon": "LON"},
    ]
    for v in vocab:
        try:
            lat = obj[v["lat"]]
            lon = obj[v["lon"]]
            if (np.size(lat) > 1) and (np.size(lon) > 1):
                lat = np.atleast_1d(lat)
                lon = np.atleast_1d(lon)
            return lat, lon
        except KeyError:
            pass
    raise LookupError


def extract_coordinates(obj, attrs=None, latname=None, lonname=None):
    """Extract the coordinates from a given object or explicitly given attrs

    The coordinates, latitude and longitude, are usually one point for the
    dataset, such as a mooring or a CTD cast, or a sequence of coordinates
    such as the alongtrack of a TSG. This function searches for the
    coordinates associated with a dataset.

    It will return the first found followin the priority:
    - Latitude and longitude items contained in the object (ex.: alongtrack).
    - Latitude and longitude as items of the given attr.
    - Latitude and longitude as items of the obj.attrs (ex.: xr.Dataset of a mooring).

    Parameters
    ----------
    obj :
    attrs :
    latname : str
        Name of the latitude variable
    lonname : str
        Name of the longitude variable
    """
    try:
        return _coordinate_flex_vocabulary(obj, latname, lonname)
    except LookupError:
        pass
    if attrs is not None:
        try:
            return _coordinate_flex_vocabulary(attrs, latname, lonname)
        except LookupError:
            pass
    if hasattr(obj, "attrs"):
        try:
            return _coordinate_flex_vocabulary(obj.attrs, latname, lonname)
        except LookupError:
            pass

    raise LookupError


def _time_flex_vocabulary(obj, varname=None):
    if varname is not None:
        try:
            t = obj[varname]
        except KeyError:
            raise LookupError
        return t

    vocab = ("time", "TIME", "date", "datetime")
    for v in vocab:
        try:
            t = obj[v]
            if np.size(t) > 1:
                t = np.atleast_1d(t).astype("datetime64[s]")
            return t
        except KeyError:
            module_logger.debug("Couldn't extract time as '{}'".format(v))
    raise LookupError


def extract_time(obj, attrs=None, varname=None):
    """Extract time from the given object or an explicitly given attrs

    It will return the first found following the priority:
    - Time item contained in the object (ex.: alongtrack).
    - Time item of a given attrs.
    - Time item of the obj.attrs (ex.: xr.Dataset of a mooring).
    """
    try:
        return _time_flex_vocabulary(obj, varname)
    except LookupError:
        module_logger.debug("Missing time in data, i.e. one time per measurement like a timeseries")
    if attrs is not None:
        try:
            return _time_flex_vocabulary(attrs, varname)
        except LookupError:
            module_logger.debug("Missing time in explicitly give attrs: {}".format(attrs))
    if hasattr(obj, "attrs"):
        try:
            return _time_flex_vocabulary(obj.attrs, varname)
        except LookupError:
            module_logger.debug("Missing time in obj's method attrs: {}".format(obj.attrs))

    raise LookupError


# ============================================================================
def savePQCCollection_pandas(db, filename):
    """ Save

        To Do:
            - Save the files in a tmp file
            - As it saves, creates a md5 of each file
            - Put everything together in a tar.bz2, including the md5 list
            - Delete the tmp file
    """
    import os
    import tempfile
    import tarfile
    import shutil
    import hashlib

    # tar = tarfile.open("%s.tar.bz2" % filename, "w:bz2")
    tar = tarfile.open(filename, "w:bz2")
    tmpdir = tempfile.mkdtemp()

    try:
        # Data
        f = "%s/data.hdf" % (tmpdir)
        db.data.to_hdf(f, "df")
        tar.add(f, arcname="data.hdf")
        # hashlib.md5(open(f, 'rb').read()).digest()
        # hashlib.sha256(open(f, 'rb').read()).digest()
        # Flags
        p = os.path.join(tmpdir, "flags")
        os.mkdir(p)
        for k in db.flags.keys():
            f = os.path.join(p, "flags_%s.hdf" % k)
            db.flags[k].to_hdf(f, "df")
            tar.add(f, arcname="flags/flags_%s.hdf" % k)
        if hasattr(db, "auxiliary"):
            p = os.path.join(tmpdir, "aux")
            os.mkdir(p)
            for k in db.auxiliary.keys():
                f = os.path.join(p, "aux_%s.hdf" % k)
                db.auxiliary[k].to_hdf(f, "df")
                tar.add(f, arcname="aux/aux_%s.hdf" % k)
        tar.close()
    except:
        shutil.rmtree(tmpdir)
        raise
        print("Problems saving the data")
        shutil.rmtree("%s.tar.bz2" % filename)
    finally:
        shutil.rmtree(tmpdir)


def loadPQCCollection_pandas(filename):
    import os
    import tempfile
    import tarfile
    import shutil

    tmpdir = tempfile.mkdtemp()
    tar = tarfile.open(filename, "r:*")
    tar.extractall(path=tmpdir)
    shutil.rmtree(tmpdir)
