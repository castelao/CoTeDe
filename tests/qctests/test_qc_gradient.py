#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

import numpy as np
from numpy import ma

from cotede.qctests import Gradient
from data import DummyData


def test():
    profile = DummyData()

    feature = ma.masked_array([0, 1.25, 5.875, 0],
            mask=[True, False, False, True])

    cfg = {'threshold': 6, 'flag_good': 1, 'flag_bad': 4}

    y = Gradient(profile, 'TEMP', cfg)
    y.test()

    assert type(y.features) is dict
    assert ma.allclose(y.features['gradient'], feature)
    assert ma.allclose(y.flags['gradient'],
            np.array([0, 1, 1, 0], dtype='i1'))
