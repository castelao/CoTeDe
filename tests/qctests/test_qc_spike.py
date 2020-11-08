#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Verify Spike QC test
"""

import numpy as np
from numpy import ma
from cotede.qctests import Spike, spike
from data import DummyData

from .compare import compare_feature_input_types, compare_input_types


def test_spike():
    """Basic test on feature spike
    """
    x = [1, -1, 2, 2, 3, 2, 4]
    y = spike(x)

    output = [np.nan, 2.0, 0.0, 0.0, 1.0, 1.0, np.nan]

    assert isinstance(y, np.ndarray)
    assert np.allclose(y, output, equal_nan=True)


def test_feature_input_types():
    x = np.array([1, -1, 2, 2, 3, 2, 4])
    compare_feature_input_types(spike, x)


def test_standard_dataset():
    """Test Spike procedure with a standard dataset
    """
    profile = DummyData()

    features = {
        "spike": [
            np.nan,
            1.78e-15,
            0.0,
            -0.03,
            -0.32,
            -1.53,
            -1.61,
            -2.56,
            -2.56,
            -4.15,
            1.00,
            1.00,
            -2.13,
            np.nan,
            np.nan,
        ]
    }
    flags = {"spike": [0, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1, 1, 1, 0, 9]}

    cfg = {"threshold": 4}

    y = Spike(profile, "TEMP", cfg)

    for f in features:
        assert np.allclose(y.features[f], features[f], equal_nan=True)
    for f in flags:
        assert np.allclose(y.flags[f], flags[f], equal_nan=True)


def test_input_types():
    cfg = {"threshold": 4}
    compare_input_types(Spike, cfg)
