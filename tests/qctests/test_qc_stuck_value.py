# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
"""

import numpy as np
from numpy import ma

from cotede.qctests import StuckValue
from ..data import DummyData


def test_default():
    profile = DummyData()
    cfg = {'flag_good': 1, 'flag_bad': 4}
    y = StuckValue(profile, 'TEMP', cfg)

    assert type(y.features) is dict
    idx = ma.getmaskarray(profile['TEMP'])
    assert (y.flags['stuck_value'][idx] == 9).all()
    assert (y.flags['stuck_value'][~idx] == 1).all()

def test_constant():
    profile = DummyData()
    profile['TEMP'][:] = profile['TEMP'] * 0 + 3.14
    cfg = {'flag_good': 1, 'flag_bad': 4}
    y = StuckValue(profile, 'TEMP', cfg)

    assert type(y.features) is dict
    idx = ma.getmaskarray(profile['TEMP'])
    assert (y.flags['stuck_value'][idx] == 9).all()
    assert (y.flags['stuck_value'][~idx] == 4).all()

def test_neglible_difference():
    profile = DummyData()
    profile['TEMP'][:] = profile['TEMP'] * 0 + 3.14
    profile['TEMP'][:] += np.random.randn(profile['TEMP'].size) * 1e-10
    cfg = {'flag_good': 1, 'flag_bad': 4}
    y = StuckValue(profile, 'TEMP', cfg)

    assert type(y.features) is dict
    idx = ma.getmaskarray(profile['TEMP'])
    assert (y.flags['stuck_value'][idx] == 9).all()
    assert (y.flags['stuck_value'][~idx] == 4).all()
