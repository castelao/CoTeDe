#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""

    Based on Timms 2011, p9597

    RoC(t) = x(t) - x(t-1)

"""

import numpy as np
from numpy import ma


def rate_of_change(x):
    y = ma.fix_invalid(np.ones_like(x) * np.nan)
    y[1:] = ma.diff(x)

    return y


class RateOfChange(object):
    def __init__(self, data, varname, cfg, autoflag=True):
        self.data = data
        self.varname = varname
        self.cfg = cfg

        self.set_features()
        if autoflag:
            self.test()

    def keys(self):
        return self.features.keys() + \
            ["flag_%s" % f for f in self.flags.keys()]

    def set_features(self):
        self.features = {
                'rate_of_change': rate_of_change(self.data[self.varname])}

    def test(self):
        self.flags = {}
        try:
            threshold = self.cfg['threshold']
        except:
            print("Deprecated cfg format. It should contain a threshold item.")
            threshold = self.cfg

        try:
            flag_good = self.cfg['flag_good']
        except:
            flag_good = 1
        try:
            flag_bad = self.cfg['flag_bad']
        except:
            flag_bad = 4

        assert (np.size(threshold) == 1) \
            and (threshold is not None) \
            and (np.isfinite(threshold))

        flag = np.zeros(self.data[self.varname].shape, dtype='i1')
        idx = ma.absolute(self.features['rate_of_change']) > threshold
        flag[np.nonzero(idx)] = flag_bad
        idx = ma.absolute(self.features['rate_of_change']) <= threshold
        flag[np.nonzero(idx)] = flag_good
        flag[ma.getmaskarray(self.data[self.varname])] = 9
        self.flags['rate_of_change'] = flag
