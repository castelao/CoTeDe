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
try:
    import shapely.wkt
    from shapely.geometry import Point
except ImportError:
    module_logger.debug("Module Shapely is not available")


class RegionalRange(QCCheckVar):
    """
        Two ways, define region with a wkt polygon or define the vertices of a simple rectangle

        Example of config:

        [{"name": "red_sea",
          "region": "POLYGON ((10, 40, 20, 50, 30, 30, 10, 40))",
          "minval": 21.7,
          "maxval": 40
          }]

    """

    def test(self):
        self.flags = {}

        feature = self.data[self.varname]

        try:
            import shapely
        except ImportError:
            module_logger.debug(
                "Regional range currently depends on module Shapely, which is not available. Regional range will return flag 0."
            )
            self.flags["regional_range"] = np.zeros(feature.shape, dtype="i1")
            return

        if ("LATITUDE" in self.data.keys()) and ("LONGITUDE" in self.data.keys()):
            lat = self.data["LATITUDE"]
            lon = self.data["LONGITUDE"]

            module_logger.warning("I'm not ready to handle regional range of a track")
            return
        elif ("LATITUDE" in self.data.attrs) and ("LONGITUDE" in self.data.attrs):
            lat = self.data.attrs["LATITUDE"]
            lon = self.data.attrs["LONGITUDE"]
        else:
            self.flags["regional_range"] = np.zeros(feature.shape, dtype="i1")
            return

        assert "regions" in self.cfg

        flag = np.zeros(feature.shape, dtype="i1")
        for cfg in self.cfg['regions']:

            assert "name" in cfg, "Regional Range must have a name"

            assert ("minval" in cfg) and (
                "maxval" in cfg
            ), "Missing limits: minval & maxval"

            minval = cfg["minval"]
            maxval = cfg["maxval"]

            assert minval < maxval, (
                "Regional Range(%s): "
                + "minval (%s) must be smaller than maxval(%s)" % (v, minval, maxval)
            )

            g = shapely.wkt.loads(cfg["region"])
            if g.intersects(Point(lon, lat)):
                flag[np.nonzero(feature < minval)] = self.flag_bad
                flag[np.nonzero(feature > maxval)] = self.flag_bad
                idx = (feature >= minval) & (feature <= maxval)
                idx = idx & (flag < self.flag_good)
                flag[np.nonzero(idx)] = self.flag_good
        flag[ma.getmaskarray(self.data[self.varname])] = 9
        self.flags["regional_range"] = flag
