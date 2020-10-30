#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Verify Rate of Change QC test
"""

import numpy as np
from numpy import ma
from cotede.qctests import RateOfChange, rate_of_change
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


def test_rate_of_change():
    """Basic test on feature rate of change
    """
    x = [1, -1, 2, 2, 3, 2, 4]
    y = rate_of_change(x)

    output = [np.nan, -2.0, 3.0, 0.0, 1.0, -1.0, 2.0]

    assert isinstance(y, np.ndarray)
    assert np.allclose(y, output, equal_nan=True)


def test_standard_dataset():
    """Test RateOfChange procedure with a standard dataset
    """
    profile = DummyData()

    features = {
        "rate_of_change": [
            np.nan,
            0.02,
            0.0,
            -0.03,
            -0.32,
            -1.53,
            -1.61,
            -3.9,
            -2.56,
            -4.31,
            -4.15,
            1,
            -2.22,
            -2.13,
            np.nan,
        ]
    }
    flags = {"rate_of_change": [0, 1, 1, 1, 1, 1, 1, 1, 1, 4, 4, 1, 1, 1, 9]}

    cfg = {"threshold": 4, "flag_good": 1, "flag_bad": 4}

    y = RateOfChange(profile, "TEMP", cfg)

    for f in features:
        assert np.allclose(y.features[f], features[f], equal_nan=True)
    for f in flags:
        assert np.allclose(y.flags[f], flags[f], equal_nan=True)


def test_tuple():
    """Test RateOfChange with a dictionary of tuples
    """
    cfg = {"threshold": 4}

    profile = DummyData()
    tp = {}
    for v in profile.keys():
        if isinstance(profile[v], ma.MaskedArray) and profile[v].mask.any():
            profile[v][profile[v].mask] = np.nan
            profile.data[v] = profile[v].data
        tp[v] = tuple(profile.data[v])

    y = RateOfChange(profile, "TEMP", cfg)
    y2 = RateOfChange(tp, "TEMP", cfg)

    for f in y.features:
        assert np.allclose(y.features[f], y2.features[f], equal_nan=True)
    for f in y.flags:
        assert np.allclose(y.flags[f], y2.flags[f], equal_nan=True)


def test_pandas():
    """Test RateOfChange with pandas.DataFrame
    """
    if not PANDAS_AVAILABLE:
        return

    cfg = {"threshold": 4}

    profile = DummyData()
    df = pd.DataFrame(profile.data)

    y = RateOfChange(profile, "TEMP", cfg)
    y2 = RateOfChange(df, "TEMP", cfg)

    for f in y.features:
        assert np.allclose(y.features[f], y2.features[f], equal_nan=True)
    for f in y.flags:
        assert np.allclose(y.flags[f], y2.flags[f], equal_nan=True)


def test_xarray():
    """Test RateOfChange with xarray.Dataset
    """
    if not XARRAY_AVAILABLE:
        return

    cfg = {"threshold": 4}

    profile = DummyData()
    ds = pd.DataFrame(profile.data).to_xarray()

    y = RateOfChange(profile, "TEMP", cfg)
    y2 = RateOfChange(ds, "TEMP", cfg)

    for f in y.features:
        assert np.allclose(y.features[f], y2.features[f], equal_nan=True)
    for f in y.flags:
        assert np.allclose(y.flags[f], y2.flags[f], equal_nan=True)
