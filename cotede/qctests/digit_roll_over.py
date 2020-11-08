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

        assert (
            (np.size(threshold) == 1)
            and (threshold is not None)
            and (np.isfinite(threshold))
        )

        feature = ma.absolute(self.features["rate_of_change"])

        flag = np.zeros(np.shape(self.data[self.varname]), dtype="i1")
        flag[feature > threshold] = self.flag_bad
        flag[feature <= threshold] = self.flag_good
        x = np.atleast_1d(self.data[self.varname])
        flag[ma.getmaskarray(x) | ~np.isfinite(x)] = 9
        self.flags["digit_roll_over"] = flag
