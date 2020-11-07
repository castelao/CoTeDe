# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
"""

import numpy as np

from cotede.qctests.profile_envelop import ProfileEnvelop
from data import DummyData

from .compare import compare_input_types


try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import xarray as xr

    XARRAY_AVAILABLE = True
except ImportError:
    XARRAY_AVAILABLE = False


def notest_profile_envelop():
    profile = DummyData()

    cfg = {"layers": [["> 0", "<= 25", -2, 37], ["> 25", "<= 50", -2, 36]]}

    flags = profile_envelop(profile, cfg, "TEMP")

    # Check for BUG #9.
    assert 9 in flags


def test_standard_dataset():
    """Test ProfileEnvelop QC procedure with standard dataset

    Also tets a case with depths not included in the layers definition, thus
    it should return flag 0, i.e. not evaluated on those depths.
    """
    profile = DummyData()

    flags = {"profile_envelop": [1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 4, 1, 9]}

    cfg = {
        "layers": [
            ["> 0", "<= 149", -2, 37],
            ["> 150", "<= 999", -2, 33],
            ["> 999", "<= 12000", -1.5, 4],
        ]
    }

    y = ProfileEnvelop(profile, varname="TEMP", cfg=cfg)

    assert hasattr(y, "flags")
    for f in flags:
        assert f in y.flags, "Missing flag {}".format(f)
        assert np.allclose(y.flags[f], flags[f], equal_nan=True)


def test_input_types():
    cfg = {
        "layers": [
            ["> 0", "<= 149", -2, 37],
            ["> 150", "<= 999", -2, 33],
            ["> 999", "<= 12000", -1.5, 4],
        ]
    }

    compare_input_types(ProfileEnvelop, cfg)
