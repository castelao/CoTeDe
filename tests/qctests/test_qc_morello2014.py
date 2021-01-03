# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

""" Check morello2014 test
"""

import numpy as np

from cotede.qctests import Morello2014
from ..data import DummyData


def test_standard_dataset():
    """Check Morello2014 with the standard dataset
    """
    cfg = {
        "procedure": "Morello2014",
        "output": {"low": None, "high": None},
        "features": {
            "spike": {"weight": 1, "low": [0.07, 0.2], "high": [2, 6]},
            "woa_normbias": {"weight": 1, "low": [3, 4], "high": [5, 6]},
            "gradient": {"weight": 1, "low": [0.5, 1.5], "high": [3, 4]},
        },
    }

    flags = {
        "morello2014": np.array(
            [1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 2, 3, 1, 1, 0], dtype="i1"
        )
    }

    profile = DummyData()

    y = Morello2014(profile, "TEMP", cfg, autoflag=True)

    assert "morello2014" in y.flags

    assert np.shape(profile["TEMP"]) == np.shape(y.flags["morello2014"])

    for f in flags:
        assert np.allclose(y.flags[f], flags[f], equal_nan=True)

    # assert sorted(np.unique(pqc.flags['TEMP']['morello2014'])) == [1, 2, 3, 4]
    # assert sorted(np.unique(pqc.flags['TEMP2']['morello2014'])) == [1]
    # assert sorted(np.unique(pqc.flags['PSAL']['morello2014'])) == [1, 2, 4]
    # assert sorted(np.unique(pqc.flags['PSAL2']['morello2014'])) == [1]
