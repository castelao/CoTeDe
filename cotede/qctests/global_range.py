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

def global_range(data, v, cfg):
    """
    """
    assert cfg['minval'] < cfg['maxval'], \
            "Global Range(%s), minval (%s) must be smaller than maxval(%s)" \
            % (v, cfg['minval'], cfg['maxval'])

    # Default flag 0, no QC.
    flag = np.zeros(data[v].shape, dtype='i1')

    # Flag good inside acceptable range
    ind = (data[v] >= cfg['minval']) & \
            (data[v] <= cfg['maxval'])
    flag[np.nonzero(ind)] = 1

    # Flag bad outside acceptable range
    ind = (data[v] < cfg['minval']) | \
        (data[v] > cfg['maxval'])
    flag[np.nonzero(ind)] = 4

    # Flag as 9 any masked input value
    flag[ma.getmaskarray(data[v])] = 9

    return flag
