# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
"""

import numpy as np
from numpy import ma

from cotede.qctests import GradientDepthConditional
from data import DummyData

from .compare import compare_input_types


def test():
    profile = DummyData()

    cfg = {
        "pressure_threshold": 400,
        "shallow_max": 9,
        "deep_max": 2.5,
        "flag_good": 1,
        "flag_bad": 4,
    }

    y = GradientDepthConditional(profile, "TEMP", cfg)

    assert isinstance(y.features, dict)
    assert "gradient" in y.features
    assert np.allclose(
        y.flags["gradient_depthconditional"],
        np.array([0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1, 1, 0, 9], dtype="i1"),
    )


def test_input_types():
    cfg = {
        "pressure_threshold": 400,
        "shallow_max": 9,
        "deep_max": 2.5,
    }
    compare_input_types(GradientDepthConditional, cfg)
