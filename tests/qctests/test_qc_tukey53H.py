#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

import numpy as np

from cotede.qctests import Tukey53H
from data import DummyData


def test_standard_dataset():
    """Test Tukey53H with a standard dataset
    """
    profile = DummyData()

    features = {
        "tukey53H": np.array(
            [
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                0.3025,
                0.02,
                0.5725,
                -0.335,
                0.4375,
                -0.29,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
            ]
        ),
        "tukey53H_norm": np.array(
            [
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                0.04145785,
                0.00274101,
                0.07846155,
                -0.045912,
                0.0599597,
                -0.03974471,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
            ]
        ),
    }
    flags = {
        "tukey53H": np.array(
            [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 9], dtype="i1"
        )
    }

    cfg = {"l": 5, "threshold": 6}

    y = Tukey53H(profile, "TEMP", cfg, autoflag=True)

    assert type(y.features) is dict
    for f in y.features:
        assert np.allclose(y.features[f], features[f], equal_nan=True)
    for f in y.flags:
        assert np.allclose(y.flags[f], flags[f], equal_nan=True)
