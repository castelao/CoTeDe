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

        flag = np.zeros(self.data[self.varname].shape, dtype="i1")
        feature = self.features["spike"]

        # ---- Shallow zone -----------------
        threshold = self.cfg["shallow_max"]
        flag[
            np.nonzero(
                (self["PRES"] <= self.cfg["pressure_threshold"]) & (feature > threshold)
            )
        ] = self.flag_bad
        flag[
            np.nonzero(
                (self["PRES"] <= self.cfg["pressure_threshold"])
                & (feature <= threshold)
            )
        ] = self.flag_good
        # ---- Deep zone --------------------
        threshold = self.cfg["deep_max"]
        flag[
            np.nonzero(
                (self["PRES"] > self.cfg["pressure_threshold"]) & (feature > threshold)
            )
        ] = self.flag_bad
        flag[
            np.nonzero(
                (self["PRES"] > self.cfg["pressure_threshold"]) & (feature <= threshold)
            )
        ] = self.flag_good

        flag[ma.getmaskarray(self.data[self.varname])] = 9
        self.flags["spike_depthconditional"] = flag
