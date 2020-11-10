# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
"""

import numpy as np
from numpy import ma

from cotede.qctests import DigitRollOver
from ..data import DummyData

from .compare import compare_input_types


def test_input_types():
    cfg = {"threshold": 3}
    compare_input_types(DigitRollOver, cfg)


def test_standard_dataset():
    profile = DummyData()

    features = {
        "rate_of_change": [
            np.nan,
            0.02,
            0.0,
            -0.03,
            -0.32,
            -1.53,
            -1.61,
            -3.9,
            -2.56,
            -4.31,
            -4.15,
            1,
            -2.22,
            -2.13,
            np.nan,
        ]
    }
    flags = {"digit_roll_over": [0, 1, 1, 1, 1, 1, 1, 4, 4, 4, 4, 1, 1, 1, 9]}

    cfg = {"threshold": 2.5}

    y = DigitRollOver(profile, "TEMP", cfg)

    for f in features:
        assert np.allclose(y.features[f], features[f], equal_nan=True)
    for f in flags:
        assert not isinstance(y.flags[f], np.ma.MaskedArray)
        assert np.allclose(y.flags[f], flags[f], equal_nan=True)
