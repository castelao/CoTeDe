# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
"""

import numpy as np
from numpy import ma

from cotede.qctests.gradient import curvature, _curvature_pandas
from cotede.qctests import Gradient
from ..data import DummyData

from .compare import compare_feature_input_types, compare_input_types


def test_curvature():
    """Basic test on feature curvature
    """
    x = [1, -1, 2, 2, 3, 2, 4]
    y = curvature(x)

    output = [np.nan, -2.5, 1.5, -0.5, 1.0, -1.5, np.nan]

    assert isinstance(y, np.ndarray)
    assert np.allclose(y, output, equal_nan=True)


def test_feature_input_types():
    x = np.array([1, -1, 2, 2, 3, 2, 4])
    compare_feature_input_types(curvature, x)


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
    flags = {"gradient": [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 4, 1, 0, 9]}

    cfg = {"threshold": 1.5}

    y = Gradient(profile, "TEMP", cfg)

    for f in features:
        assert np.allclose(y.features[f], features[f], equal_nan=True)
    for f in flags:
        assert np.allclose(y.flags[f], flags[f], equal_nan=True)


def test_input_types():
    cfg = {"threshold": 4}
    compare_input_types(Gradient, cfg)
