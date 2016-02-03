#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

import numpy as np
from numpy import ma

from cotede.qctests import Gradient


def test():
    dummy_data = {
        'PRES': ma.masked_array([0.0, 100, 500, 5000]),
        'TEMP': ma.masked_array([25.16, 19.73, 10.80, 2.12]),
        'PSAL': ma.masked_array([32.00, 34.74, 34.66, 35.03])
        }
    feature = ma.masked_array([0, 1.75, 0.125, 0],
            mask=[True, False, False, True])

    cfg = {
            'threshold': 6,
            'flag_good': 1,
            'flag_bad': 4
            }

    y = Gradient(dummy_data, 'TEMP', cfg)
    y.test()

    assert type(y.features) is dict
    assert ma.allclose(y.features['gradient'], feature)
    assert ma.allclose(y.flags['gradient'],
            np.array([0, 1, 1, 0], dtype='i1'))
