#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""

    Based on Timms 2011, p9597

    RoC(t) = x(t) - x(t-1)

"""

import logging

import numpy as np
from numpy import ma

from .qctests import QCCheckVar


module_logger = logging.getLogger(__name__)


def rate_of_change(x):
    if isinstance(x, ma.MaskedArray):
        x[x.mask] = np.nan
        x = x.data

    y = np.nan * np.atleast_1d(x)
    y[1:] = np.diff(x)

    return y


class RateOfChange(QCCheckVar):
    def set_features(self):
        self.features = {"rate_of_change": rate_of_change(self.data[self.varname])}

    def test(self):
        self.flags = {}
        try:
            threshold = self.cfg["threshold"]
        except KeyError:
            print("Deprecated cfg format. It should contain a threshold item.")
            threshold = self.cfg

        assert (
            (np.size(threshold) == 1)
            and (threshold is not None)
            and (np.isfinite(threshold))
        )

        feature = np.absolute(self.features["rate_of_change"])
        if ("sd_scale" in self.cfg) and self.cfg["sd_scale"]:
            feature /= feature.std()

        flag = np.zeros(np.shape(self.data[self.varname]), dtype="i1")
        flag[feature > threshold] = self.flag_bad
        flag[feature <= threshold] = self.flag_good
        x = np.atleast_1d(self.data[self.varname])
        flag[ma.getmaskarray(x) | ~np.isfinite(x)] = 9
        self.flags["rate_of_change"] = flag
