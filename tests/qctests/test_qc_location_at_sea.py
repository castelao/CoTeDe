#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Consistency check for location at sea QC test.

Create tests to evaluate lat > 90, lat < -90, lon < -180, lon > 360
  for get_bathymetry and for LocationAtSea
"""

import numpy as np
from numpy import ma

from cotede.qctests.location_at_sea import (
    extract_coordinates,
    LocationAtSea,
    location_at_sea,
    get_bathymetry,
)
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

try:
    import oceansdb

    OCEANSDB_AVAILABLE = True
except ImportError:
    OCEANSDB_AVAILABLE = False


def test_extract_standard_dataset():
    profile = DummyData()
    lat, lon = extract_coordinates(profile)
    assert lat == 15
    assert lon == -38


def test_extract_data_scalar_standard_dataset():
    profile = DummyData()
    profile.data["lat"] = 0
    profile.data["lon"] = -32
    lat, lon = extract_coordinates(profile)
    assert lat == 0
    assert lon == -32


def test_extract_data_sequence_standard_dataset():
    lat = [0, 0, 8]
    lon = [-32, -38, -38]

    profile = DummyData()
    profile.data["lat"] = lat
    profile.data["lon"] = lon
    lat2, lon2 = extract_coordinates(profile)
    assert np.allclose(lat, lat2, equal_nan=True)
    assert np.allclose(lon, lon2, equal_nan=True)


def test_extract_pandas():
    if not PANDAS_AVAILABLE:
        return

    lat = [0, 0, 8]
    lon = [-32, -38, -38]

    df = pd.DataFrame({"lat": lat, "lon": lon})
    lat2, lon2 = extract_coordinates(df)
    assert np.allclose(lat, lat2, equal_nan=True)
    assert np.allclose(lon, lon2, equal_nan=True)


def test_extract_xarray():
    if not XARRAY_AVAILABLE:
        return

    lat = [0, 0, 8]
    lon = [-32, -38, -38]

    ds = xr.Dataset({"lat": lat, "lon": lon})
    lat2, lon2 = extract_coordinates(ds)
    assert np.allclose(lat, lat2, equal_nan=True)
    assert np.allclose(lon, lon2, equal_nan=True)


def test_bathymetry_point():
    """Check the elevation of single locations
    """
    if not OCEANSDB_AVAILABLE:
        return

    coords = [[10, 30, -366], [10, -30, 5192], [15, -38, 5036], [12, 222, 4995]]
    for lat, lon, z in coords:
        etopo = get_bathymetry(lat, lon, resolution="5min")

        assert "bathymetry" in etopo, "Missing bathymetry from get_bathymetry"
        assert ma.allclose(etopo["bathymetry"], [z]), "For ({},{}) expected {}".format(
            lat, lon, z
        )


def test_bathymetry_track():
    """Check the elevation for a track
    """
    if not OCEANSDB_AVAILABLE:
        return

    lat = [10, 10, 15, 12]
    lon = [30, -30, -38, 222]
    z = [-366, 5192, 5036, 4995]
    etopo = get_bathymetry(lat, lon, resolution="5min")

    assert "bathymetry" in etopo, "Missing bathymetry from get_bathymetry"
    assert ma.allclose(etopo["bathymetry"], z), "Unexpected value"


def test_bathymetry_greenwich():
    """Check elevation that includes 0
    """
    if not OCEANSDB_AVAILABLE:
        return

    coords = [[0, 0, 4876], [6, 0, -76], [-10, 0, 5454]]
    for lat, lon, z in coords:
        etopo = get_bathymetry(lat, lon, resolution="5min")
        assert "bathymetry" in etopo, "Missing bathymetry from get_bathymetry"
        assert ma.allclose(etopo["bathymetry"], [z]), "For ({},{}) expected {}".format(
            lat, lon, z
        )


def test_attribute():
    if not OCEANSDB_AVAILABLE:
        return

    data = DummyData()

    coords = [[10, -30, 1], [10, 330, 1]]
    for lat, lon, flag in coords:
        data.attrs["LATITUDE"] = lat
        data.attrs["LONGITUDE"] = lon
        assert location_at_sea(data) == flag


def test_attribute_inland():
    if not OCEANSDB_AVAILABLE:
        return

    data = DummyData()

    coords = [[-10, -60, 3], [-10, 300, 3]]
    for lat, lon, flag in coords:
        data.attrs["LATITUDE"] = lat
        data.attrs["LONGITUDE"] = lon
        assert location_at_sea(data) == flag


def test_data():
    if not OCEANSDB_AVAILABLE:
        return

    data = DummyData()

    data.data["LATITUDE"] = 10
    data.data["LONGITUDE"] = -30
    flag = location_at_sea(data)
    assert flag == 1

    data.data["LATITUDE"] = 10
    data.data["LONGITUDE"] = 330
    flag = location_at_sea(data)
    assert flag == 1


def test_badlocation():
    if not OCEANSDB_AVAILABLE:
        return

    data = DummyData()

    coords = [[91, -30, 3], [-91, -30, 3], [10, -361, 3], [10, 1000, 3]]
    for lat, lon, flag in coords:
        data.attrs["LATITUDE"] = lat
        data.attrs["LONGITUDE"] = lon
        assert location_at_sea(data) == flag


def test_nonelocation():
    if not OCEANSDB_AVAILABLE:
        return

    data = DummyData()

    coords = [[None, 1, 0], [1, None, 0]]
    for lat, lon, flag in coords:
        data.attrs["LATITUDE"] = lat
        data.attrs["LONGITUDE"] = lon
        assert location_at_sea(data) == flag

    del data.attrs["LATITUDE"]
    data.attrs["LONGITUDE"] = 1
    assert location_at_sea(data) == 0

    del data.attrs["LONGITUDE"]
    data.attrs["LATITUDE"] = 1
    assert location_at_sea(data) == 0


def test_LocationAtSea_attrs():
    """Test standard with single location

       Lat & Lon defined in the attrs

       Locking etopo resolution, since it can change the values.
    """
    if not OCEANSDB_AVAILABLE:
        return

    data = DummyData()
    y = LocationAtSea(data, cfg={"resolution": "5min"})

    assert hasattr(y, "features")
    assert "bathymetry" in y.features
    assert ma.allclose(y.features["bathymetry"], 5036)
    assert hasattr(y, "flags")
    assert "location_at_sea" in y.flags
    assert ma.allclose(y.flags["location_at_sea"], 1)


def test_LocationAtSea_track():
    """Test standard with multiple locations

       lat & lon defined in the dataset. This would be the case for a TSG
       where each measurement is associated with a location.

       Locking etopo resolution, since it can change the values.

       Note that there is no restriction in the number of locations. In this
       example there are multiple depths but only 3 positions. It's not the
       LocationAtSea job to make sense of that. Should it match with which
       variable? It can't be done here, but should be done once the tests
       are combined.
    """
    if not OCEANSDB_AVAILABLE:
        return

    data = DummyData()
    data.data["LATITUDE"] = [15, 12, 8]
    data.data["LONGITUDE"] = [-38, 222, 0]

    y = LocationAtSea(data, cfg={"resolution": "5min"})

    assert hasattr(y, "features")
    assert "bathymetry" in y.features
    assert ma.allclose(y.features["bathymetry"], [5036, 4995, -122])
    assert hasattr(y, "flags")
    assert "location_at_sea" in y.flags
    assert np.allclose(y.flags["location_at_sea"], [1, 1, 3])


def test_LocationAtSea_track_pandas_noattrs():
    """Equivalent to test_LocationAtSea_track but using pandas
    """
    if not PANDAS_AVAILABLE or not OCEANSDB_AVAILABLE:
        return

    data = pd.DataFrame(DummyData().data)
    data["LATITUDE"] = 15
    data["LONGITUDE"] = -38

    y = LocationAtSea(data, cfg={"resolution": "5min"})


def test_compare_pandas():
    """Validate the results using pandas.DataFrame
    """
    if not PANDAS_AVAILABLE or not OCEANSDB_AVAILABLE:
        return

    profile = DummyData()
    df = pd.DataFrame(profile.data)

    Procedure = LocationAtSea
    y = Procedure(profile)
    y2 = Procedure(df, attrs=profile.attrs)

    for f in y.features:
        assert np.allclose(y.features[f], y2.features[f], equal_nan=True)
        assert np.shape(y.features[f]) == np.shape(y2.features[f])
    for f in y.flags:
        assert type(y.flags[f]) == type(y2.flags[f])
        assert y.flags[f].dtype == y2.flags[f].dtype
        assert np.allclose(y.flags[f], y2.flags[f], equal_nan=True)


def test_compare_xarray():
    """Validate the results using xarray.Dataset
    """
    if not XARRAY_AVAILABLE or not OCEANSDB_AVAILABLE:
        return

    profile = DummyData()
    ds = xr.Dataset(profile.data)
    for a in profile.attrs:
        ds.attrs[a] = profile.attrs[a]

    Procedure = LocationAtSea
    y = Procedure(profile)
    y2 = Procedure(ds)

    for f in y.features:
        assert np.allclose(y.features[f], y2.features[f], equal_nan=True)
    for f in y.flags:
        assert type(y.flags[f]) == type(y2.flags[f])
        assert y.flags[f].dtype == y2.flags[f].dtype
        assert np.allclose(y.flags[f], y2.flags[f], equal_nan=True)
