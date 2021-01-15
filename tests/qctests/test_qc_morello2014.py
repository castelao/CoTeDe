# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

""" Check morello2014 test
"""

import numpy as np

from cotede.qc import ProfileQC
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
            [0, 1, 1, 1, 1, 1, 2, 1, 1, 1, 2, 3, 1, 0, 0], dtype="i1"
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


def test_morello_from_profileqc():
    """Run Morello2014 through ProfileQC

    Notes
    -----
    - There is room to improve this and verify more stuff
    """
    cfg = {
        "TEMP": {
            "morello2014": {
                "procedure": "Morello2014",
                "output": {"low": None, "high": None},
                "features": {
                    "spike": {"weight": 1, "low": [0.07, 0.2], "high": [2, 6]},
                    "woa_normbias": {"weight": 1, "low": [3, 4], "high": [5, 6]},
                    "gradient": {"weight": 1, "low": [0.5, 1.5], "high": [3, 4]},
                },
            }
        },
        "PSAL": {
            "morello2014": {
                "output": {"low": None, "high": None},
                "features": {
                    "spike": {"weight": 1, "low": [0.05, 0.15], "high": [0.5, 0.9]},
                    "woa_normbias": {"weight": 1, "low": [3, 4], "high": [5, 6]},
                    "gradient": {"weight": 1, "low": [1, 2], "high": [3, 4]},
                },
            }
        },
    }

    profile = DummyData()
    pqc = ProfileQC(profile, cfg="morello2014")

    for v in ("TEMP", "PSAL"):
        assert "morello2014" in pqc.flags[v]
