#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""

    ATENTION: Create test for global_range
    - masked values
    - input np.array
    - properly handle inf, nan?
"""

import numpy as np
from numpy import ma


class GlobalRange(object):
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
        self.features = {}

    def test(self):
        self.flags = {}
        assert ('minval' in self.cfg) and ('maxval' in self.cfg), \
                "Missing limits: minval & maxval"

        assert self.cfg['minval'] < self.cfg['maxval'], "Global Range(%s): " \
                + "minval (%s) must be smaller than maxval(%s)" \
                % (v, self.cfg['minval'], self.cfg['maxval'])

        minval = self.cfg['minval']
        maxval = self.cfg['maxval']

        try:
            flag_good = self.cfg['flag_good']
        except:
            flag_good = 1
        try:
            flag_bad = self.cfg['flag_bad']
        except:
            flag_bad = 4

        flag = np.zeros(self.data[self.varname].shape, dtype='i1')

        idx = self.data[self.varname] < minval
        flag[np.nonzero(idx)] = flag_bad

        idx = self.data[self.varname] > maxval
        flag[np.nonzero(idx)] = flag_bad

        idx = (self.data[self.varname] >= minval) \
                & (self.data[self.varname] <= maxval)
        flag[np.nonzero(idx)] = flag_good

        flag[ma.getmaskarray(self.data[self.varname])] = 9

        self.flags['global_range'] = flag
