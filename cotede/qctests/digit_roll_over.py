#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""

   Argo, test #12. (10C, 5PSU)

"""

import logging

import numpy as np
from numpy import ma

from .qctests import QCCheckVar
from .rate_of_change import rate_of_change


module_logger = logging.getLogger(__name__)


class DigitRollOver(QCCheckVar):
    def set_features(self):
        self.features = {"rate_of_change": rate_of_change(self.data[self.varname])}

    def test(self):
        self.flags = {}
        try:
            threshold = self.cfg["threshold"]
        except KeyError:
            module_logger.debug(
                "Deprecated cfg format. It should contain a threshold item."
            )
            threshold = self.cfg

        try:
            flag_good = self.cfg["flag_good"]
        except KeyError:
            flag_good = 1
        try:
            flag_bad = self.cfg["flag_bad"]
        except KeyError:
            flag_bad = 4

        assert (
            (np.size(threshold) == 1)
            and (threshold is not None)
            and (np.isfinite(threshold))
        )

        flag = np.zeros(self.data[self.varname].shape, dtype="i1")
        feature = ma.absolute(self.features["rate_of_change"])
        flag[np.nonzero(feature > threshold)] = self.flag_bad
        flag[np.nonzero(feature <= threshold)] = self.flag_good
        flag[ma.getmaskarray(self.data[self.varname])] = 9
        self.flags["digit_roll_over"] = flag
