# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst


import logging

import numpy as np
from numpy import ma

from .qctests import QCCheckVar

module_logger = logging.getLogger(__name__)


class StuckValue(QCCheckVar):
    def test(self):
        self.flags = {}

        x = ma.compressed(self.data[self.varname])
        flag = np.zeros(self.data[self.varname].shape, dtype='i1')
        if (x.size > 1) and (np.allclose(x, np.ones_like(x) * x[0])):
            flag[:] = self.flag_bad
        else:
            flag[:] = self.flag_good
        flag[ma.getmaskarray(self.data[self.varname])] = 9
        self.flags['stuck_value'] = flag
