
import numpy as np
from numpy import ma

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


def compare_feature_tuple(feature, x):
    """Validate a feature from a tuple

    Compare a feature defined from a numpy.array versus the same
    feature from a tuple
    """
    tp = tuple(x)
    y = feature(x)
    y2 = feature(tp)

    assert isinstance(y, np.ndarray)
    assert np.allclose(y, y2, equal_nan=True)


def compare_feature_series(feature, x):
    """Validate a feature from a pandas.Series

    Compare a feature defined from a numpy.array versus the same
    feature from a pandas.Series
    """
    if not PANDAS_AVAILABLE:
        return
    ds = pd.Series(x)
    y = feature(x)
    y2 = feature(ds)

    assert type(x) != type(ds)
    assert isinstance(y, np.ndarray)
    assert np.allclose(y, y2, equal_nan=True)


def compare_feature_dataarray(feature, x):
    """Validate a feature from a xarray.DataArray

    Compare a feature defined from a numpy.array versus the same
    feature from a xarray.DataArray
    """
    if not XARRAY_AVAILABLE:
        return
    da = xr.DataArray(x)
    y = feature(x)
    y2 = feature(da)

    assert type(x) != type(da)
    assert isinstance(y, np.ndarray)
    assert np.allclose(y, y2, equal_nan=True)


def compare_feature_input_types(feature, x):
    compare_feature_tuple(feature, x)
    compare_feature_series(feature, x)
    compare_feature_dataarray(feature, x)


def compare_tuple(Procedure, cfg):
    """Validate the results using a tuple
    """
    profile = DummyData()
    tp = {}
    for v in profile.keys():
        if isinstance(profile[v], ma.MaskedArray) and profile[v].mask.any():
            profile[v][profile[v].mask] = np.nan
            profile.data[v] = profile[v].data
        tp[v] = tuple(profile.data[v])

    y = Procedure(profile, "TEMP", cfg)
    y2 = Procedure(tp, "TEMP", cfg)

    assert isinstance(y2["TEMP"], tuple), "It didn't preserve the tuple type"

    for f in y.features:
        assert np.allclose(y.features[f], y2.features[f], equal_nan=True)
        assert y.features[f].dtype == y2.features[f].dtype
    for f in y.flags:
        assert np.allclose(y.flags[f], y2.flags[f], equal_nan=True)
        assert y.flags[f].dtype == y2.flags[f].dtype


def compare_pandas(Procedure, cfg):
    """Validate the results using pandas.DataFrame
    """
    if not PANDAS_AVAILABLE:
        return

    profile = DummyData()
    df = pd.DataFrame(profile.data)

    y = Procedure(profile, "TEMP", cfg)
    y2 = Procedure(df, "TEMP", cfg)

    for f in y.features:
        assert np.allclose(y.features[f], y2.features[f], equal_nan=True)
    for f in y.flags:
        assert np.allclose(y.flags[f], y2.flags[f], equal_nan=True)


def compare_xarray(Procedure, cfg):
    """Validate the results using pandas.DataFrame
    """
    if not XARRAY_AVAILABLE:
        return

    profile = DummyData()
    ds = pd.DataFrame(profile.data).to_xarray()

    y = Procedure(profile, "TEMP", cfg)
    y2 = Procedure(ds, "TEMP", cfg)

    for f in y.features:
        assert np.allclose(y.features[f], y2.features[f], equal_nan=True)
    for f in y.flags:
        assert np.allclose(y.flags[f], y2.flags[f], equal_nan=True)


def compare_input_types(feature, cfg):
    compare_tuple(feature, cfg)
    compare_pandas(feature, cfg)
    compare_xarray(feature, cfg)
