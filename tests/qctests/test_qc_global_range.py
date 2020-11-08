#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Verify Rate of Change QC test
"""

import numpy as np
from numpy import ma
from cotede.qctests import GlobalRange
from data import DummyData

from .compare import compare_feature_input_types, compare_input_types


def test_standard_dataset():
    """Test GlobalRange procedure with a standard dataset
    """
    profile = DummyData()

    flags = {"global_range": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 9]}

    cfg = {"threshold": 4, "minval": -2.5, "maxval": 40.0}

    y = GlobalRange(profile, "TEMP", cfg)

    for f in flags:
        assert np.allclose(y.flags[f], flags[f], equal_nan=True)


def test_input_types():
    cfg = {"threshold": 4, "minval": -2.5, "maxval": 40.0}
    compare_input_types(GlobalRange, cfg)
