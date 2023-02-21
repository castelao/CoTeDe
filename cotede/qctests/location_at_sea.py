# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""Evaluates if the coordinates of the measurements are at sea

The heavy lift of this procedure is done by an external package OceansDB, which
interpolates the elevation for given coordinates.
"""

import logging

import numpy as np
from numpy import ma

from .qctests import QCCheck
from ..utils import extract_coordinates

module_logger = logging.getLogger(__name__)

try:
    import oceansdb

    OCEANSDB_AVAILABLE = True
except ImportError:
    module_logger.debug("OceansDB package is not available")
    OCEANSDB_AVAILABLE = False


def location_at_sea(data, cfg=None):
    """ Evaluate if location is at sea.

        Interpolate the depth from ETOPO for the data position.
          If local "height" is negative, means lower than sea
          level, hence at sea.

        FIXME: It must allow to check Lat/Lon from data to work with
          TSGs, i.e. one location for each measurement.
          Double check other branches, I thought I had already done
            this before.

    ATTENTION: This is old code that was completely replaced by LocationAtSea
    and it will be removed.
    """
    try:
        flag_good = cfg["flag_good"]
    except:
        flag_good = 1
    try:
        flag_bad = cfg["flag_bad"]
    except:
        flag_bad = 3

    assert hasattr(data, "attrs"), "Missing attributes"

    # Temporary solution while migrating to OceanSites variables syntax
    if ("LATITUDE" not in data.attrs) and ("latitude" in data.attrs):
        module_logger.debug(
            "Deprecated. In the future it will not accept latitude anymore. It'll must be LATITUDE"
        )
        data.attrs["LATITUDE"] = data.attrs["latitude"]
    if ("LONGITUDE" not in data.attrs) and ("longitude" in data.attrs):
        module_logger.debug(
            "Deprecated. In the future it will not accept longitude anymore. It'll must be LONGITUDE"
        )
        data.attrs["LONGITUDE"] = data.attrs["longitude"]

    if (
        ("LATITUDE" not in data.attrs)
        or (data.attrs["LATITUDE"] == None)
        or ("LONGITUDE" not in data.attrs)
        or (data.attrs["LONGITUDE"] == None)
    ):
        module_logger.debug("Missing geolocation (lat/lon)")
        return 0

    if (
        (data.attrs["LATITUDE"] > 90)
        or (data.attrs["LATITUDE"] < -90)
        or (data.attrs["LONGITUDE"] > 360)
        or (data.attrs["LONGITUDE"] < -180)
    ):
        return flag_bad

    try:
        etopo = None
        with oceansdb.ETOPO() as ETOPO:
            etopo = ETOPO["topography"].extract(
                var="height", lat=data.attrs["LATITUDE"], lon=data.attrs["LONGITUDE"]
            )
        h = etopo["height"]

        flag = np.zeros(h.shape, dtype="i1")
        flag[np.nonzero(h <= 0)] = flag_good
        flag[np.nonzero(h > 0)] = flag_bad

        return flag

    except:
        return 0

def _get_etopo(db, lat, lon):
    return db["topography"].track(var="height", lat=lat, lon=lon)

def get_bathymetry(lat, lon, resolution="5min", etopo_dbs=None):
    """Interpolate bathymetry from ETOPO

       For a given (lat, lon), interpolates the bathymetry from ETOPO
    """
    assert np.shape(lat) == np.shape(lon), "Lat & Lon shape mismatch"

    etopo = None
    if etopo_dbs is None:
        with oceansdb.ETOPO(resolution=resolution) as db:
            etopo = _get_etopo(db, lat, lon)
    else:
        etopo = _get_etopo(etopo_dbs[resolution], lat, lon)

    return {"bathymetry": -etopo["height"].astype("i")}


class LocationAtSea(QCCheck):
    flag_bad = 3
    resolution = "5min"
    threshold = 0

    def __init__(self, data, cfg=None, attrs=None, cars_db=None, woa_db=None, etopo_dbs=None):
        if cfg is None:
            cfg = {}

        if "threshold" not in cfg:
            cfg["threshold"] = self.threshold
        if "resolution" not in cfg:
            cfg["resolution"] = self.resolution
        super().__init__(data, cfg=cfg, attrs=attrs, cars_db=cars_db, woa_db=woa_db, etopo_dbs=etopo_dbs)

    def set_features(self):
        if not OCEANSDB_AVAILABLE:
            module_logger.warning("LocationAtSea requires OceansDB!")

        try:
            # Note that QCCheck fallback to self.data.attrs if attrs not given
            lat, lon = extract_coordinates(self.data, self.attrs)
        except LookupError:
            module_logger.warning("Missing geolocation (lat/lon)")
            self.features = {}
            return

        try:
            self.features = get_bathymetry(lat=lat, lon=lon, etopo_dbs=self._etopo_dbs)
            # idx = np.isfinite(lat) & np.isfinite(lon)
            # self.features = get_bathymetry(lat=lat[idx], lon=lon[idx])
        except:
            self.features = {
                "bathymetry": np.nan * lat,
                "bathymetry_std": np.nan * lat,
            }

    def test(self):
        self.flags = {}
        try:
            threshold = self.cfg["threshold"]
        except KeyError:
            module_logger.info("No threshold for location at sea. I'll use 0")
            threshold = 0

        if "bathymetry" not in self.features:
            self.flags["location_at_sea"] = 0
            return

        feature = np.atleast_1d(self.features["bathymetry"])

        flag = np.zeros(np.shape(feature), dtype="i1")
        flag[feature < threshold] = self.flag_bad
        flag[feature >= threshold] = self.flag_good
        self.flags["location_at_sea"] = flag
