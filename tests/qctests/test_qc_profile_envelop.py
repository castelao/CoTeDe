# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
"""

import numpy as np

from cotede.qctests.profile_envelop import ProfileEnvelop, profile_envelop
from data import DummyData


def test():
    profile = DummyData()

    cfg = {"layers": [["> 0", "<= 25", -2, 37], ["> 25", "<= 50", -2, 36]]}

    flags = profile_envelop(profile, cfg, "TEMP")

    # Check for BUG #9.
    assert 9 in flags


def test_class():
    """

       ATTENTION, unrealistic limits used just for testing purposes.
    """
    data = DummyData()
    cfg = {
        "layers": [
            ["> 0", "<= 149", -2, 37],
            ["> 150", "<= 999", -2, 33],
            ["> 999", "<= 12000", -1.5, 4],
        ]
    }
    y = ProfileEnvelop(data, varname="TEMP", cfg=cfg)

    assert hasattr(y, "features")
    assert hasattr(y, "flags")

    assert np.all(
        y.flags["profile_envelop"] == [1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 4, 1, 9]
    )
