#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""

    ATENTION: Create test for global_range
    - masked values
    - input np.array
    - properly handle inf, nan?
"""

import logging

import numpy as np
from numpy import ma

from .qctests import QCCheckVar


module_logger = logging.getLogger(__name__)


class GlobalRange(QCCheckVar):
    def test(self):
        self.flags = {}
        assert ("minval" in self.cfg) and (
            "maxval" in self.cfg
        ), "Missing limits: minval & maxval"

        assert self.cfg["minval"] < self.cfg["maxval"], (
            "Global Range(%s): "
            + "minval (%s) must be smaller than maxval(%s)"
            % (v, self.cfg["minval"], self.cfg["maxval"])
        )

        minval = self.cfg["minval"]
        maxval = self.cfg["maxval"]

        feature = self.data[self.varname]

        flag = np.zeros(feature.shape, dtype="i1")
        flag[np.nonzero(feature < minval)] = self.flag_bad
        flag[np.nonzero(feature > maxval)] = self.flag_bad
        idx = (feature >= minval) & (feature <= maxval)
        flag[np.nonzero(idx)] = self.flag_good
        flag[ma.getmaskarray(self.data[self.varname])] = 9
        self.flags['global_range'] = flag
