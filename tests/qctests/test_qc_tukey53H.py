#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

import numpy as np
from numpy import ma

from cotede.qctests import Tukey53H
from data import DummyData


def test():
    profile = DummyData()

    profile.data['PRES'] = ma.masked_array([1.0, 100, 200, 300, 500, 5000])
    profile.data['TEMP'] = ma.masked_array([27.44, 14.55, 11.96, 11.02, 7.65, 2.12])
    profile.data['PSAL'] = ma.masked_array([35.71, 35.50, 35.13, 35.02, 34.72, 35.03])

    features = {
            'tukey53H': ma.masked_array([0, 0, 0.3525000000000009,
                0.35249999999999915, 0, 0],
                mask=[True, True, False, False, True, True]),
            'tukey53H_norm': ma.masked_array([0, 0, 0.07388721803621254,
                0.07388721803621218, 0, 0],
                mask = [True,  True, False, False, True, True])
            }
    flags = {'tukey53H_norm': np.array([0, 0, 1, 1, 0, 0], dtype='i1')}

    cfg = {
            'l': 5,
            'threshold': 6,
            'flag_good': 1,
            'flag_bad': 4
            }

    y = Tukey53H(profile, 'TEMP', cfg)
    y.test()

    assert type(y.features) is dict
    for f in y.features:
        assert ma.allclose(y.features[f], features[f])
    for f in y.flags:
        assert ma.allclose(y.flags[f], flags[f])
