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

from cotede.qctests import QCCheckVar


module_logger = logging.getLogger(__name__)


def rate_of_change(x):
    if isinstance(x, ma.MaskedArray):
        x[x.mask] = np.nan
        x = x.data

    y = x * np.nan
    y[1:] = np.diff(x)

    return y


class RateOfChange(QCCheckVar):
    def set_features(self):
        x = ma.fix_invalid(self.data[self.varname])
        self.features = {'rate_of_change': rate_of_change(x)}

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

        feature = np.absolute(self.features['rate_of_change'])
        if ('sd_scale' in self.cfg) and self.cfg['sd_scale']:
            feature /= feature.std()

        flag = np.zeros(self.data[self.varname].shape, dtype='i1')
        flag[np.nonzero(feature > threshold)] = self.flag_bad
        flag[np.nonzero(feature <= threshold)] = self.flag_good
        x = self.data[self.varname]
        flag[ma.getmaskarray(x) | ~np.isfinite(x)] = 9
        self.flags['rate_of_change'] = flag
