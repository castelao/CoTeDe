#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""

"""

import logging

import numpy as np
from numpy import ma

from .qctests import QCCheckVar
from .gradient import curvature

module_logger = logging.getLogger(__name__)


class GradientDepthConditional(QCCheckVar):
    def set_features(self):
        self.features = {"gradient": curvature(self.data[self.varname])}

    def test(self):
        self.flags = {}

        flag = np.zeros(self.data[self.varname].shape, dtype="i1")
        feature = np.absolute(self.features["gradient"])

        # ---- Shallow zone -----------------
        threshold = self.cfg["shallow_max"]
        flag[np.nonzero(
                (self["PRES"] <= self.cfg["pressure_threshold"])
                & (feature > threshold)
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
                (self["PRES"] > self.cfg["pressure_threshold"])
                & (feature > threshold)
            )
        ] = self.flag_bad
        flag[
            np.nonzero(
                (self["PRES"] > self.cfg["pressure_threshold"])
                & (feature <= threshold)
            )
        ] = self.flag_good

        x = self.data[self.varname]
        flag[ma.getmaskarray(x) | ~np.isfinite(x)] = 9
        self.flags["gradient_depthconditional"] = flag
