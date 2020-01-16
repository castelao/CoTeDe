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

def gradient(x):
    """ Gradient QC

        This is different the mathematical gradient:
        d/dx + d/dy + d/dz,
        but as defined by GTSPP, EuroGOOS and others.
    """
    y = ma.fix_invalid(np.ones_like(x) * np.nan)
    y[1:-1] = np.abs(x[1:-1] - (x[:-2] + x[2:]) / 2.0)
    return y


class Gradient(QCCheckVar):
    def set_features(self):
        self.features = {"gradient": gradient(self.data[self.varname])}

    def test(self):
        self.flags = {}
        try:
            threshold = self.cfg["threshold"]
        except KeyError:
            module_logger.debug(
                "Deprecated cfg format. It should contain a threshold item."
            )
            threshold = self.cfg

        assert (
            (np.size(threshold) == 1)
            and (threshold is not None)
            and (np.isfinite(threshold))
        )

        flag = np.zeros(self.data[self.varname].shape, dtype="i1")
        feature = self.features["gradient"]
        flag[np.nonzero(feature > threshold)] = self.flag_bad
        flag[np.nonzero(feature <= threshold)] = self.flag_good
        flag[ma.getmaskarray(self.data[self.varname])] = 9
        self.flags["gradient"] = flag
