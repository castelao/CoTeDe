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
    y = ma.fix_invalid(np.ones_like(x) * np.nan)
    y[1:] = ma.diff(x)

    return y


class RateOfChange(QCCheckVar):
    def set_features(self):
        self.features = {
                'rate_of_change': rate_of_change(self.data[self.varname])}

    def test(self):
        self.flags = {}
        try:
            threshold = self.cfg['threshold']
        except KeyError:
            print("Deprecated cfg format. It should contain a threshold item.")
            threshold = self.cfg

        assert (np.size(threshold) == 1) \
            and (threshold is not None) \
            and (np.isfinite(threshold))

        flag = np.zeros(self.data[self.varname].shape, dtype='i1')
        feature = ma.absolute(self.features['rate_of_change'])
        flag[np.nonzero(feature > threshold)] = self.flag_bad
        flag[np.nonzero(feature <= threshold)] = self.flag_good
        flag[ma.getmaskarray(self.data[self.varname])] = 9
        self.flags['rate_of_change'] = flag
