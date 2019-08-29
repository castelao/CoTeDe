# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst


import logging

import numpy as np
from numpy import ma

module_logger = logging.getLogger(__name__)


class StuckValue(object):
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

        try:
            flag_good = self.cfg['flag_good']
        except:
            flag_good = 1
        try:
            flag_bad = self.cfg['flag_bad']
        except:
            flag_bad = 4

        x = ma.compressed(self.data[self.varname])
        flag = np.zeros(self.data[self.varname].shape, dtype='i1')
        if (x.size > 1) and (np.allclose(x, np.ones_like(x) * x[0])):
            flag[:] = flag_bad
        else:
            flag[:] = flag_good
        flag[ma.getmaskarray(self.data[self.varname])] = 9
        self.flags['stuck_value'] = flag
