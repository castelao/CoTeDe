#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""

Threshold - |median(v0..v4)| + |sigma(v0..v4)|
y = ma.masked_all_like(x)
yy = np.stack([x[:-4], x[1:-3], x[2:-2], x[3:-1], x[4:]])
y[2:-2] = np.median(yy, axis=0) + yy.std(axis=0)
y = np.stack([x[:-4], x[1:-3], x[2:-2], x[3:-1], x[4:]])
"""

import logging

import numpy as np
from numpy import ma

from .qctests import QCCheckVar


module_logger = logging.getLogger(__name__)


def spike(x):
    """ Spike
    """
    if isinstance(x, ma.MaskedArray):
        mask = x.mask
        x = x.data
        x[mask] = np.nan

    y = np.nan * x
    y[1:-1] = np.abs(x[1:-1] - (x[:-2] + x[2:]) / 2.0) - np.abs((x[2:] - x[:-2]) / 2.0)
    return y


class Spike(QCCheckVar):
    def set_features(self):
        self.features = {"spike": spike(self.data[self.varname])}

    def test(self):
        self.flags = {}
        try:
            threshold = self.cfg["threshold"]
        except KeyError:
            module_logger.warning(
                "Deprecated cfg format. It should contain a threshold item."
            )
            threshold = self.cfg

        assert (
            (np.size(threshold) == 1)
            and (threshold is not None)
            and (np.isfinite(threshold))
        )

        flag = np.zeros(self.data[self.varname].shape, dtype="i1")
        feature = np.absolute(self.features["spike"])
        flag[np.nonzero(feature > threshold)] = self.flag_bad
        flag[np.nonzero(feature <= threshold)] = self.flag_good
        # Flag as 9 any masked input value
        x = self.data[self.varname]
        flag[ma.getmaskarray(x) | ~np.isfinite(x)] = 9
        self.flags["spike"] = flag
