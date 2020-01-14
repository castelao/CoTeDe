#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""

"""

import logging

import numpy as np
from numpy import ma

from .qctests import QCCheckVar

module_logger = logging.getLogger(__name__)


def valid_geolocation(lat, lon):
    if np.shape(lat) != np.shape(lon):
        return False

    idx = (
        ma.greater_equal(lat, -90)
        & ma.less_equal(lat, 90)
        & ma.greater_equal(lon, -180)
        & ma.less_equal(lon, 360)
    )
    return idx


class ValidGeolocation(QCCheckVar):
    def test(self):
        self.flags = {}

        if ("LATITUDE" in self.data.keys()) and ("LONGITUDE" in self.data.keys()):
            lat = self.data["LATITUDE"]
            lon = self.data["LONGITUDE"]
        elif ("LATITUDE" in self.data.attrs) and ("LONGITUDE" in self.data.attrs):
            lat = self.data.attrs["LATITUDE"]
            lon = self.data.attrs["LONGITUDE"]
        else:
            self.flags["valid_position"] = self.flag_bad
            return

        idx = valid_geolocation(lat, lon)
        flag = np.zeros(np.shape(idx), dtype="i1")
        flag[~idx] = self.flag_bad
        flag[idx] = self.flag_good
        flag[ma.getmaskarray(idx)] = 9
        self.flags["valid_geolocation"] = flag
