#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Verify the Cummulative Rate of Change QC test
"""

import numpy as np
from cotede.qctests import CumRateOfChange, cum_rate_of_change
from ..data import DummyData


def test_cum_rate_of_change():
    x = [1, -1, 2, 2, 3, 2, 4]
    memory = 0.8
    y = cum_rate_of_change(x, memory)

    output = [np.nan, 2.0, 3.0, 2.4, 2.12, 1.896, 2.0]

    assert isinstance(y, np.ndarray)
    assert np.allclose(y, output, equal_nan=True)


def test_standard_dataset():
    """Test CumRateOfChange with a standard dataset
    """
    profile = DummyData()

    features = {
        "cum_rate_of_change": [
            np.nan,
            0.02,
            0.016,
            0.03,
            0.32,
            1.53,
            1.61,
            3.9,
            3.632,
            4.31,
            4.278,
            3.6224,
            3.34192,
            3.099536,
            np.nan,
        ]
    }
    flags = {"cum_rate_of_change": [0, 1, 1, 1, 1, 1, 1, 1, 1, 4, 4, 1, 1, 1, 9]}

    cfg = {"memory": 0.8, "threshold": 4, "flag_good": 1, "flag_bad": 4}

    y = CumRateOfChange(profile, "TEMP", cfg)

    for f in features:
        assert np.allclose(y.features[f], features[f], equal_nan=True)
    for f in flags:
        assert np.allclose(y.flags[f], flags[f], equal_nan=True)
