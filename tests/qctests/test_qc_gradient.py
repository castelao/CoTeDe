# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
"""

import numpy as np
from numpy import ma

from cotede.qctests.gradient import curvature, _curvature_pandas
from cotede.qctests import Gradient
from data import DummyData


def test_standard_dataset():
    profile = DummyData()

    features = {
        "gradient": np.array(
            [
                np.nan,
                0.01,
                0.015,
                0.145,
                0.605,
                0.04,
                1.145,
                -0.67,
                0.875,
                -0.08,
                -2.575,
                1.61,
                -0.045,
                np.nan,
                np.nan,
            ]
        )
    }
    flags = {
        "gradient": np.array([0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 4, 1, 0, 9], dtype="i1")
    }

    cfg = {"threshold": 1.5, "flag_good": 1, "flag_bad": 4}

    y = Gradient(profile, "TEMP", cfg, autoflag=True)

    assert type(y.features) is dict
    for f in y.features:
        assert np.allclose(y.features[f], features[f], equal_nan=True)
    for f in y.flags:
        assert np.allclose(y.flags[f], flags[f], equal_nan=True)


def test_numpy_vs_pandas():
    """Confirm that the two curvature give the same results
    """
    profile = DummyData()
    n = curvature(profile["TEMP"])
    p = _curvature_pandas(profile["TEMP"])
    assert np.allclose(n, p, equal_nan=True)
