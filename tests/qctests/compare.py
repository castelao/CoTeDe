import numpy as np
from numpy import ma

from ..data import DummyData

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


def compare_feature_tuple(feature, *args, **kwargs):
    """Validate a feature from a tuple

    Compare a feature defined from a numpy.array versus the same
    feature from a tuple
    """
    tp_args = [tuple(x) for x in args]
    tp_kwargs = {}
    for v in kwargs:
        tp_kwargs[v] = tuple(kwargs[v])

    y = feature(*args, **kwargs)
    y2 = feature(*tp_args, **tp_kwargs)

    assert isinstance(y, np.ndarray)
    assert np.allclose(y, y2, equal_nan=True)


def compare_feature_series(feature, *args, **kwargs):
    """Validate a feature from a pandas.Series

    Compare a feature defined from a numpy.array versus the same
    feature from a pandas.Series
    """
    if not PANDAS_AVAILABLE:
        return

    ds_args = [pd.Series(x) for x in args]
    ds_kwargs = {}
    for v in kwargs:
        ds_kwargs[v] = pd.Series(kwargs[v])

    y = feature(*args, **kwargs)
    y2 = feature(*ds_args, **ds_kwargs)

    for x, ds in zip(args, ds_args):
        assert type(x) != type(ds)
    for x, ds in zip(kwargs, ds_kwargs):
        assert type(kwargs[x]) != type(ds_kwargs[ds])
    assert isinstance(y, np.ndarray)
    assert np.allclose(y, y2, equal_nan=True)


def compare_feature_dataarray(feature, *args, **kwargs):
    """Validate a feature from a xarray.DataArray

    Compare a feature defined from a numpy.array versus the same
    feature from a xarray.DataArray
    """
    if not XARRAY_AVAILABLE:
        return

    da_args = [xr.DataArray(x) for x in args]
    da_kwargs = {}
    for v in kwargs:
        da_kwargs[v] = xr.DataArray(kwargs[v])

    y = feature(*args, **kwargs)
    y2 = feature(*da_args, **da_kwargs)

    for x, da in zip(args, da_args):
        assert type(x) != type(da)
    for x, da in zip(kwargs, da_kwargs):
        assert type(kwargs[x]) != type(da_kwargs[da])
    assert isinstance(y, np.ndarray)
    assert np.allclose(y, y2, equal_nan=True)


def compare_feature_input_types(feature, *args, **kwargs):
    compare_feature_tuple(feature, *args, **kwargs)
    compare_feature_series(feature, *args, **kwargs)
    compare_feature_dataarray(feature, *args, **kwargs)


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
        assert type(y.flags[f]) == type(y2.flags[f])
        assert y.flags[f].dtype == y2.flags[f].dtype
        assert np.allclose(y.flags[f], y2.flags[f], equal_nan=True)


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
        assert type(y.flags[f]) == type(y2.flags[f])
        assert y.flags[f].dtype == y2.flags[f].dtype
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
        assert type(y.flags[f]) == type(y2.flags[f])
        assert y.flags[f].dtype == y2.flags[f].dtype
        assert np.allclose(y.flags[f], y2.flags[f], equal_nan=True)


def compare_input_types(feature, cfg):
    compare_tuple(feature, cfg)
    compare_pandas(feature, cfg)
    compare_xarray(feature, cfg)
