# -*- coding: utf-8 -*-

import logging

import numpy as np
from numpy import ma

from .qctests import QCCheck

module_logger = logging.getLogger(__name__)

try:
    import oceansdb
except ImportError:
    module_logger.debug("OceansDB package is not available")


def location_at_sea(data, cfg=None):
    """ Evaluate if location is at sea.

        Interpolate the depth from ETOPO for the data position.
          If local "height" is negative, means lower than sea
          level, hence at sea.

        FIXME: It must allow to check Lat/Lon from data to work with
          TSGs, i.e. one location for each measurement.
          Double check other branches, I thought I had already done
            this before.
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
    if ('LATITUDE' not in data.attrs) and ('latitude' in data.attrs):
                module_logger.debug("Deprecated. In the future it will not accept latitude anymore. It'll must be LATITUDE")
                data.attrs['LATITUDE'] = data.attrs['latitude']
    if ('LONGITUDE' not in data.attrs) and ('longitude' in data.attrs):
                module_logger.debug("Deprecated. In the future it will not accept longitude anymore. It'll must be LONGITUDE")
                data.attrs['LONGITUDE'] = data.attrs['longitude']

    if ('LATITUDE' not in data.attrs) or \
            (data.attrs['LATITUDE'] == None) or \
            ('LONGITUDE' not in data.attrs) or \
            (data.attrs['LONGITUDE'] == None):
                module_logger.debug("Missing geolocation (lat/lon)")
                return 0

    if (data.attrs['LATITUDE'] > 90) or \
            (data.attrs['LATITUDE'] < -90) or \
            (data.attrs['LONGITUDE'] > 360) or \
            (data.attrs['LONGITUDE'] < -180):
                return flag_bad

    try:
        ETOPO = oceansdb.ETOPO()
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


def get_bathymetry(lat, lon, resolution="5min"):
    """Interpolate bathymetry from ETOPO

       For a given (lat, lon), interpolates the bathymetry from ETOPO
    """
    assert np.shape(lat) == np.shape(lon), "Lat & Lon shape mismatch"

    db = oceansdb.ETOPO(resolution=resolution)

    etopo = db["topography"].track(var="height", lat=lat, lon=lon)
    return {"bathymetry": -etopo["height"].astype("i")}


class LocationAtSea(QCCheck):
    def set_features(self):
        if ("LATITUDE" in self.data.keys()) and ("LONGITUDE" in self.data.keys()):
            lat = self.data["LATITUDE"]
            lon = self.data["LONGITUDE"]
        elif ("LATITUDE" in self.data.attrs) and ("LONGITUDE" in self.data.attrs):
            lat = self.data.attrs["LATITUDE"]
            lon = self.data.attrs["LONGITUDE"]
        else:
            module_logger.debug("Missing geolocation (lat/lon)")
            self.features = {}
            return

        try:
            self.features = get_bathymetry(lat=lat, lon=lon)
        except:
            self.features = {
                "bathymetry": ma.fix_invalid([np.nan]),
                "bathymetry_std": ma.fix_invalid([np.nan]),
            }
        return

        if (
            ("LATITUDE" not in self.data.attrs)
            or (self.data.attrs["LATITUDE"] is None)
            or ("LONGITUDE" not in self.data.attrs)
            or (self.data.attrs["LONGITUDE"] is None)
        ):
            module_logger.debug("Missing geolocation (lat/lon)")
            self.features = {
                "bathymetry": ma.fix_invalid([np.nan]),
                "bathymetry_std": ma.fix_invalid([np.nan]),
            }
            self.flags["valid_position"] = self.flag_bad
            return

        if (
            (self.data.attrs["LATITUDE"] > 90)
            or (self.data.attrs["LATITUDE"] < -90)
            or (self.data.attrs["LONGITUDE"] > 360)
            or (self.data.attrs["LONGITUDE"] < -180)
        ):
            self.features = {
                "bathymetry": ma.fix_invalid([np.nan]),
                "bathymetry_std": ma.fix_invalid([np.nan]),
            }
            return

        lat = self.data.attrs["LATITUDE"]
        lon = self.data.attrs["LONGITUDE"]
        try:
            self.features = get_bathymetry(lat=lat, lon=lon)
        except:
            self.features = {
                "bathymetry": ma.fix_invalid([np.nan]),
                "bathymetry_std": ma.fix_invalid([np.nan]),
            }

    def test(self):
        self.flags = {}
        try:
            threshold = self.cfg["threshold"]
        except KeyError:
            module_logger.debug("No threshold for location at sea. I'll use 0")
            threshold = 0

        flag = np.zeros(self.features["bathymetry"].shape, dtype="i1")
        flag[np.nonzero(self.features["bathymetry"] < threshold)] = self.flag_bad
        flag[np.nonzero(self.features["bathymetry"] >= threshold)] = self.flag_good
        flag[ma.getmaskarray(self.features["bathymetry"])] = 9
        self.flags["location_at_sea"] = flag
