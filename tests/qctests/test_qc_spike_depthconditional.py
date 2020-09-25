# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
"""

import numpy as np

from cotede.qctests import SpikeDepthConditional
from data import DummyData


def test():
    profile = DummyData()

    cfg = {
        "pressure_threshold": 400,
        "shallow_max": 6,
        "deep_max": .05,
        "flag_good": 1,
        "flag_bad": 4,
    }

    y = SpikeDepthConditional(profile, "TEMP", cfg)

    assert isinstance(y.features, dict)
    assert "spike" in y.features
    assert np.allclose(
        y.flags["spike_depthconditional"],
        np.array([0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 4, 1, 0, 9], dtype="i1"),
    )
