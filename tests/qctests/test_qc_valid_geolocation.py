#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Consistency check for valid geolocation QC test.
"""

import numpy as np
from numpy import ma

from cotede.qctests.valid_geolocation import valid_geolocation, ValidGeolocation
from ..data import DummyData

from tests.qctests.compare import compare_feature_input_types, compare_input_types

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


"""
Tests to implement:
    - missing lat, missing lon, missing both
    - single point
    - list
    - array
    - masked array
    - single point with NaN (lat, lon, lat & lon)
    - list with some NaN
        - lat lon coincident
        - lat lon non-coincident
    - masked array with some masked values
    - Greenwich

Tests on class(QCCheck)
    - lat lon in attrs
    - lat lon in data
    - invalid
        - lat
        - lon
        - lat & lon
"""


def test_valid_single_coordinate():
    coords = [[10, -30], [10, 330]]
    for lat, lon in coords:
        assert valid_geolocation(lat, lon) == True


def test_invalid_single_coordinate():
    coords = [[99, 0], [-91.1, 0], [99, 361], [0, -181], [0, 361]]
    for lat, lon in coords:
        assert valid_geolocation(lat, lon) == False


def test_nan_single_coordinate():
    coords = [[np.nan, -30], [10, np.nan]]
    for lat, lon in coords:
        assert valid_geolocation(lat, lon) == False


def test_valid_coordinate_list():
    lat = [10, 10, -15]
    lon = [-30, 330, 30]
    assert np.all(valid_geolocation(lat, lon) == True)


def test_valid_coordinate_list():
    lat = [np.nan, 10, np.nan]
    lon = [-30, np.nan, 30]
    assert np.all(valid_geolocation(lat, lon) == False)


def test_feature_input_types():
    lat = np.array([10, 10, -15, np.nan, 0, np.nan])
    lon = np.array([-30, 330, 30, 0, np.nan, np.nan])
    compare_feature_input_types(valid_geolocation, lat, lon)


def test_standard_dataset():
    profile = DummyData()
    flags = {"valid_geolocation": [1]}

    y = ValidGeolocation(profile)
    for f in flags:
        assert np.allclose(y.flags[f], flags[f], equal_nan=True)


def test_standard_dataset_alongtrack():
    profile = DummyData()
    profile.data["lat"] = profile["TEMP"] * 0
    profile.data["lon"] = profile["TEMP"] * 0

    flags = {"valid_geolocation": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3]}

    y = ValidGeolocation(profile)
    for f in flags:
        assert np.allclose(y.flags[f], flags[f], equal_nan=True)


# def test_input_types():
#     compare_input_types(ValidGeolocation)
def test_compare_tuple():
    """Validate the results using a tuple
    """
    profile = DummyData()
    profile.data["lat"] = profile["TEMP"] * 0
    profile.data["lon"] = profile["TEMP"] * 0

    tp = {}
    for v in profile.keys():
        if isinstance(profile[v], ma.MaskedArray) and profile[v].mask.any():
            profile[v][profile[v].mask] = np.nan
            profile.data[v] = profile[v].data
        tp[v] = tuple(profile.data[v])

    y = ValidGeolocation(profile)
    y2 = ValidGeolocation(tp)

    assert isinstance(y2["lat"], tuple), "It didn't preserve the tuple type"

    for f in y.features:
        assert np.allclose(y.features[f], y2.features[f], equal_nan=True)
        assert y.features[f].dtype == y2.features[f].dtype
    for f in y.flags:
        assert type(y.flags[f]) == type(y2.flags[f])
        assert y.flags[f].dtype == y2.flags[f].dtype
        assert np.allclose(y.flags[f], y2.flags[f], equal_nan=True)


def test_compare_pandas():
    """Validate the results using pandas.DataFrame
    """
    if not PANDAS_AVAILABLE:
        return

    profile = DummyData()
    profile.data["lat"] = profile["TEMP"] * 0
    profile.data["lon"] = profile["TEMP"] * 0
    df = pd.DataFrame(profile.data)

    y = ValidGeolocation(profile)
    y2 = ValidGeolocation(df)

    for f in y.features:
        assert np.allclose(y.features[f], y2.features[f], equal_nan=True)
    for f in y.flags:
        assert type(y.flags[f]) == type(y2.flags[f])
        assert y.flags[f].dtype == y2.flags[f].dtype
        assert np.allclose(y.flags[f], y2.flags[f], equal_nan=True)


def test_compare_xarray():
    """Validate the results using pandas.DataFrame
    """
    if not XARRAY_AVAILABLE:
        return

    profile = DummyData()
    profile.data["lat"] = profile["TEMP"] * 0
    profile.data["lon"] = profile["TEMP"] * 0
    ds = pd.DataFrame(profile.data).to_xarray()

    y = ValidGeolocation(profile)
    y2 = ValidGeolocation(ds)

    for f in y.features:
        assert np.allclose(y.features[f], y2.features[f], equal_nan=True)
    for f in y.flags:
        assert type(y.flags[f]) == type(y2.flags[f])
        assert y.flags[f].dtype == y2.flags[f].dtype
        assert np.allclose(y.flags[f], y2.flags[f], equal_nan=True)
