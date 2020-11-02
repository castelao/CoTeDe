#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Verify Spike QC test
"""

import numpy as np
from numpy import ma
from cotede.qctests import Spike, spike
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


def test_spike():
    """Basic test on feature rate of change
    """
    x = [1, -1, 2, 2, 3, 2, 4]
    y = spike(x)

    output = [np.nan, 2.0, 0.0, 0.0, 1.0, 1.0, np.nan]

    assert isinstance(y, np.ndarray)
    assert np.allclose(y, output, equal_nan=True)


def test_standard_dataset():
    """Test Spike procedure with a standard dataset
    """
    profile = DummyData()

    features = {
        "spike": [
            np.nan,
            1.78e-15,
            0.0,
            -0.03,
            -0.32,
            -1.53,
            -1.61,
            -2.56,
            -2.56,
            -4.15,
            1.00,
            1.00,
            -2.13,
            np.nan,
            np.nan,
        ]
    }
    flags = {"spike": [0, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1, 1, 1, 0, 9]}

    cfg = {"threshold": 4}

    y = Spike(profile, "TEMP", cfg)

    for f in features:
        assert np.allclose(y.features[f], features[f], equal_nan=True)
    for f in flags:
        assert np.allclose(y.flags[f], flags[f], equal_nan=True)


def test_tuple():
    """Test Spike with a dictionary of tuples
    """
    cfg = {"threshold": 4}

    profile = DummyData()
    tp = {}
    for v in profile.keys():
        if isinstance(profile[v], ma.MaskedArray) and profile[v].mask.any():
            profile[v][profile[v].mask] = np.nan
            profile.data[v] = profile[v].data
        tp[v] = tuple(profile.data[v])

    y = Spike(profile, "TEMP", cfg)
    y2 = Spike(tp, "TEMP", cfg)

    assert isinstance(y2["TEMP"], tuple), "It didn't preserve the tuple type"

    for f in y.features:
        assert np.allclose(y.features[f], y2.features[f], equal_nan=True)
        assert y.features[f].dtype == y2.features[f].dtype
    for f in y.flags:
        assert np.allclose(y.flags[f], y2.flags[f], equal_nan=True)
        assert y.flags[f].dtype == y2.flags[f].dtype


def test_pandas():
    """Test Spike with pandas.DataFrame
    """
    if not PANDAS_AVAILABLE:
        return

    cfg = {"threshold": 4}

    profile = DummyData()
    df = pd.DataFrame(profile.data)

    y = Spike(profile, "TEMP", cfg)
    y2 = Spike(df, "TEMP", cfg)

    for f in y.features:
        assert np.allclose(y.features[f], y2.features[f], equal_nan=True)
    for f in y.flags:
        assert np.allclose(y.flags[f], y2.flags[f], equal_nan=True)


def test_xarray():
    """Test Spike with xarray.Dataset
    """
    if not XARRAY_AVAILABLE:
        return

    cfg = {"threshold": 4}

    profile = DummyData()
    ds = pd.DataFrame(profile.data).to_xarray()

    y = Spike(profile, "TEMP", cfg)
    y2 = Spike(ds, "TEMP", cfg)

    for f in y.features:
        assert np.allclose(y.features[f], y2.features[f], equal_nan=True)
    for f in y.flags:
        assert np.allclose(y.flags[f], y2.flags[f], equal_nan=True)
