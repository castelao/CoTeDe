# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""Validate Deepest Pressure test
"""

import numpy as np
from numpy import ma

from cotede.qctests import DeepestPressure
from data import DummyData


def test_default():
    profile = DummyData()

    cfg = {'threshold': 1000}

    y = DeepestPressure(profile, 'TEMP', cfg)
    y.test()

    assert 'deepest_pressure' in y.flags
    assert profile['TEMP'].shape == y.flags['deepest_pressure'].shape

    idx = ma.getmaskarray(profile['TEMP'])
    assert idx.any(), "Redefine DummyData to have at least one masked value"
    assert np.all(y.flags['deepest_pressure'][idx] == 9)

    x = profile['PRES'][y.flags['deepest_pressure'] == 1]
    idx = (x <= 1.1 * cfg['threshold'])
    assert idx.any(), "Redefine cfg to have at least one valid value"
    assert idx.all()
    x = profile['PRES'][y.flags['deepest_pressure'] == 3]
    idx = (x > 1.1 * cfg['threshold'])
    assert idx.any(), "Redefine cfg to have at least one non-valid value"
    assert idx.all()
