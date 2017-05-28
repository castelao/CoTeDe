#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""

    Based on Timms 2011, p9597

    RoC(t) = x(t) - x(t-1)

"""

import numpy as np
from numpy import ma

def rate_of_change(data, v, cfg):

    RoC = ma.masked_all_like(data[v])
    RoC[1:] = ma.diff(data[v])

    flag = np.zeros(data[v].shape, dtype='i1')
    flag[np.nonzero(ma.absolute(RoC) <= cfg)] = 1
    flag[np.nonzero(ma.absolute(RoC) > cfg)] = 4
    flag[ma.getmaskarray(data[v])] = 9

    return flag, RoC
