#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""

"""

import logging

import numpy as np
from numpy import ma

from .qctests import QCCheckVar
from .spike import spike


module_logger = logging.getLogger(__name__)


class SpikeDepthConditional(QCCheckVar):
    def set_features(self):
        self.features = {"spike": spike(self.data[self.varname])}

    def test(self):
        self.flags = {}

        flag = np.zeros(np.shape(self.data[self.varname]), dtype="i1")
        feature = self.features["spike"]

        # ---- Shallow zone -----------------
        threshold = self.cfg["shallow_max"]
        flag[
            np.nonzero(
                (np.atleast_1d(self["PRES"]) <= self.cfg["pressure_threshold"])
                & (feature > threshold)
            )
        ] = self.flag_bad
        flag[
            np.nonzero(
                (np.atleast_1d(self["PRES"]) <= self.cfg["pressure_threshold"])
                & (feature <= threshold)
            )
        ] = self.flag_good
        # ---- Deep zone --------------------
        threshold = self.cfg["deep_max"]
        flag[
            np.nonzero(
                (np.atleast_1d(self["PRES"]) > self.cfg["pressure_threshold"])
                & (feature > threshold)
            )
        ] = self.flag_bad
        flag[
            np.nonzero(
                (np.atleast_1d(self["PRES"]) > self.cfg["pressure_threshold"])
                & (feature <= threshold)
            )
        ] = self.flag_good

        # Flag as 9 any masked input value
        x = np.atleast_1d(self.data[self.varname])
        flag[ma.getmaskarray(x) | ~np.isfinite(x)] = 9
        self.flags["spike_depthconditional"] = flag
