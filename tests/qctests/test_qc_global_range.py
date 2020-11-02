#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Verify Rate of Change QC test
"""

import numpy as np
from numpy import ma
from cotede.qctests import GlobalRange
from data import DummyData

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


def test_standard_dataset():
    """Test GlobalRange procedure with a standard dataset
    """
    profile = DummyData()

    flags = {"global_range": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 9]}

    cfg = {"threshold": 4, "minval": -2.5, "maxval": 40.0}

    y = GlobalRange(profile, "TEMP", cfg)

    for f in flags:
        assert np.allclose(y.flags[f], flags[f], equal_nan=True)


def test_tuple():
    """Test GlobalRange with a dictionary of tuples
    """
    cfg = {"threshold": 4, "minval": -2.5, "maxval": 40.0}

    profile = DummyData()
    tp = {}
    for v in profile.keys():
        if isinstance(profile[v], ma.MaskedArray) and profile[v].mask.any():
            profile[v][profile[v].mask] = np.nan
            profile.data[v] = profile[v].data
        tp[v] = tuple(profile.data[v])

    y = GlobalRange(profile, "TEMP", cfg)
    y2 = GlobalRange(tp, "TEMP", cfg)

    for f in y.flags:
        assert np.allclose(y.flags[f], y2.flags[f], equal_nan=True)


def test_pandas():
    """Test GlobalRange with pandas.DataFrame
    """
    if not PANDAS_AVAILABLE:
        return

    cfg = {"threshold": 4, "minval": -2.5, "maxval": 40.0}

    profile = DummyData()
    df = pd.DataFrame(profile.data)

    y = GlobalRange(profile, "TEMP", cfg)
    y2 = GlobalRange(df, "TEMP", cfg)

    for f in y.flags:
        assert np.allclose(y.flags[f], y2.flags[f], equal_nan=True)


def test_xarray():
    """Test GlobalRange with xarray.Dataset
    """
    if not XARRAY_AVAILABLE:
        return

    cfg = {"threshold": 4, "minval": -2.5, "maxval": 40.0}

    profile = DummyData()
    ds = pd.DataFrame(profile.data).to_xarray()

    y = GlobalRange(profile, "TEMP", cfg)
    y2 = GlobalRange(ds, "TEMP", cfg)

    for f in y.flags:
        assert np.allclose(y.flags[f], y2.flags[f], equal_nan=True)
