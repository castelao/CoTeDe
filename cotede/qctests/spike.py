#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""

"""

import numpy as np
from numpy import ma

FLAG_GOOD = 1
FLAG_BAD = 4


def spike(x):
    """ Spike
    """
    y = ma.masked_all_like(x)
    y[1:-1] = np.abs(x[1:-1] - (x[:-2] + x[2:])/2.0) - \
                np.abs((x[2:] - x[:-2])/2.0)
    return y


class Spike(object):
    def __init__(self, data, varname, cfg):
        self.data = data
        self.varname = varname
        self.cfg = cfg

        self.set_features()

    def keys(self):
        return self.features.keys() + \
            ["flag_%s" % f for f in self.flags.keys()]

    def set_features(self):
        self.features = {'spike': spike(self.data[self.varname])}

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
            flag_good = FLAG_GOOD
        try:
            flag_bad = self.cfg['flag_bad']
        except:
            flag_bad = FLAG_BAD

        assert (np.size(threshold) == 1) and \
                (threshold is not None) and \
                (np.isfinite(threshold))   

        flag = np.zeros(self.data[self.varname].shape, dtype='i1')
        flag[np.nonzero(self.features['spike'] > threshold)] = flag_bad
        flag[np.nonzero(self.features['spike'] <= threshold)] = flag_good
        flag[ma.getmaskarray(self.data[self.varname])] = 9
        self.flags['spike'] = flag
