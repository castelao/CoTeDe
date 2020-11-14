# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""Evaluates if the coordinates are valid

"""

import logging

import numpy as np
from numpy import ma

from .qctests import QCCheck
from .location_at_sea import extract_coordinates

module_logger = logging.getLogger(__name__)


def valid_geolocation(lat, lon):
    if np.shape(lat) != np.shape(lon):
        module_logger.warning("Coordinates lat & lon have inconsistent shapes")
        return False

    lat = np.atleast_1d(lat)
    lon = np.atleast_1d(lon)
    idx = (lat >= -90) & (lat <= 90) & (lon >= -180) & (lon <= 360)
    return idx


class ValidGeolocation(QCCheck):
    flag_bad = 3

    def test(self):
        self.flags = {}

        try:
            # Note that QCCheck fallback to self.data.attrs if attrs not given
            if hasattr(self, "attrs"):
                lat, lon = extract_coordinates(self.data, self.attrs)
            else:
                lat, lon = extract_coordinates(self.data)
        except LookupError:
            module_logger.warning("Missing geolocation (lat/lon)")
            self.flags["valid_position"] = self.flag_bad
            return

        idx = valid_geolocation(lat, lon)
        flag = np.zeros(np.shape(idx), dtype="i1")
        flag[~idx] = self.flag_bad
        flag[idx] = self.flag_good
        self.flags["valid_geolocation"] = flag
