#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Verify Rate of Change QC test
"""

import numpy as np
from numpy import ma
from cotede.qctests import RateOfChange, rate_of_change
from data import DummyData

from .compare import compare_feature_input_types, compare_input_types


def test_rate_of_change():
    """Basic test on feature rate of change
    """
    x = [1, -1, 2, 2, 3, 2, 4]
    y = rate_of_change(x)

    output = [np.nan, -2.0, 3.0, 0.0, 1.0, -1.0, 2.0]

    assert isinstance(y, np.ndarray)
    assert np.allclose(y, output, equal_nan=True)


def test_feature_input_types():
    x = np.array([1, -1, 2, 2, 3, 2, 4])
    compare_feature_input_types(rate_of_change, x)


def test_standard_dataset():
    """Test RateOfChange procedure with a standard dataset
    """
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
    flags = {"rate_of_change": [0, 1, 1, 1, 1, 1, 1, 1, 1, 4, 4, 1, 1, 1, 9]}

    cfg = {"threshold": 4, "flag_good": 1, "flag_bad": 4}

    y = RateOfChange(profile, "TEMP", cfg)

    for f in features:
        assert np.allclose(y.features[f], features[f], equal_nan=True)
    for f in flags:
        assert np.allclose(y.flags[f], flags[f], equal_nan=True)


def test_input_types():
    cfg = {"threshold": 4}
    compare_input_types(RateOfChange, cfg)
