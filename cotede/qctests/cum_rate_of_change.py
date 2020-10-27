# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst


"""

    Based on Timms 2011, p9597

"The first case in Equation (1) ensures that the cumulative rate of change function is able to quickly respond to degradations in sensor quality, while the second case ensures that it takes a longer time for confidence to return in the measurements from that sensor once the rate of change of the parameter decreases." (Timms 2011)

        Small   S->M            Medium          M->L            Large
Temp    <0.03   0.03 to 0.05    0.05 to 0.07    0.07 to 0.11    >0.11
Cond    <50     50 to 100       100 to 150      150 to 250      >250


Timms 2011 uses k=0.8

if (RoC_small (t) + 0.5 × RoC_medium (t)) < (cRoC_small (t - 1) + 0.5 × cRoC_medium (t - 1)):
    cRoC_i (t) = RoC_i (t)
else
    cRoC_i (t) = (1 - k) × RoC_i(t) + k * cRoC_i(t - 1)

i = small, medium, large
"""

import numpy as np
from numpy import ma
import logging

from .qctests import QCCheckVar

module_logger = logging.getLogger(__name__)

def cum_rate_of_change(x, memory):
    """Cummulative rate of change
    """
    if isinstance(x, ma.MaskedArray):
        x[x.mask] = np.nan
        x = x.data

    y = np.nan * np.ones_like(x)
    y[1:] = np.absolute(np.diff(x))

    for i in range(2, y.size):
        if y[i] < y[i - 1]:
            y[i] = (1 - memory) * y[i] + memory * y[i - 1]

    return y


class CumRateOfChange(QCCheckVar):
    def set_features(self):
        module_logger.debug("Feature: cummulative rate of change")
        self.features = {
            "cum_rate_of_change": cum_rate_of_change(
                self.data[self.varname], self.cfg["memory"]
            )
        }

    def test(self):
        self.flags = {}
        try:
            threshold = self.cfg["threshold"]
        except KeyError:
            print("Deprecated cfg format. It should contain a threshold item.")
            threshold = self.cfg

        assert np.size(threshold) == 1, "Threshold should be a single value"
        assert threshold is not None, "Threshold can't be None"
        assert np.isfinite(threshold), "Threshold must be a valid number"

        flag = np.zeros(self.data[self.varname].shape, dtype="i1")
        feature = np.absolute(self.features["cum_rate_of_change"])
        flag[np.nonzero(feature > threshold)] = self.flag_bad
        flag[np.nonzero(feature <= threshold)] = self.flag_good
        x = self.data[self.varname]
        flag[ma.getmaskarray(x) | ~np.isfinite(x)] = 9
        self.flags["cum_rate_of_change"] = flag
