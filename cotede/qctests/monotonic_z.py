#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""

8. Pressure increasing test
This test requires that the profile has pressures that are monotonically increasing (assuming the pressures are ordered from smallest to largest).
Action: If there is a region of constant pressure, all but the first of a consecutive set of constant pressures should be flagged as bad data. If there is a region where pressure reverses, all of the pressures in the reversed part of the profile should be flagged as bad data. All pressures flagged as bad data and all of the associated temperatures and salinities are removed from the TESAC distributed on the GTS.

"""

import logging

import numpy as np
from numpy import ma

from .qctests import QCCheckVar


module_logger = logging.getLogger(__name__)


class MonotonicZ(QCCheckVar):
    """Check if sensor vertical movement is monotonic

       This is usually called Increasing Depth, Increasing Pressure ...

       Most of the implementations define a stop or a invertion in the
       verticalm movement as bad data.

       cfg[coord, tolerance]
    """

    coord = "depth"

    def test(self):
        """

           coord = depth
           tolerance = 0.0
        """
        self.flags = {}

        if "coord" in self.cfg:
            self.coord = self.cfg["coord"]

        z = self[self.coord]
        assert np.shape(self[self.varname]) == np.shape(z)

        flag = np.zeros(self[self.varname].shape, dtype="i1")

        dz = np.diff(z)
        if np.all(dz > 0):
            flag[:] = self.flag_good
        else:
            flag[0] = self.flag_good
            zmax = z[0]
            for i, zn in enumerate(z[1:], 1):
                if zn > zmax:
                    zmax = zn
                    flag[i] = self.flag_good
                else:
                    flag[i] = self.flag_bad
        flag[ma.getmaskarray(z)] = 9

        if "flag_name" in self.cfg:
            flag_name = self.cfg["flag_name"]
        else:
            flag_name = "monotonic_{}".format(self.cfg["coord"].lower())
        self.flags[flag_name] = flag
