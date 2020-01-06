#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Consistency check for location at sea QC test.
"""

from numpy import ma

from cotede.qctests.location_at_sea import (
    LocationAtSea,
    location_at_sea,
    get_bathymetry,
)
from data import DummyData


def test_bathymetry_point():
    """Check the elevation of single locations
    """
    coords = [[10, 30, -366], [10, -30, 5192], [15, -38, 5036], [12, 222, 4995]]
    for lat, lon, z in coords:
        etopo = get_bathymetry(lat, lon, resolution="5min")

        assert "bathymetry" in etopo, "Missing bathymetry from get_bathymetry"
        assert ma.allclose(etopo["bathymetry"], [z]), \
                "For ({},{}) expected {}".format(lat, lon, z)


def test_bathymetry_track():
    """Check the elevation for a track
    """
    lat = [10, 10, 15, 12]
    lon = [30, -30, -38, 222]
    z = [-366, 5192, 5036, 4995]
    etopo = get_bathymetry(lat, lon, resolution="5min")

    assert "bathymetry" in etopo, "Missing bathymetry from get_bathymetry"
    assert ma.allclose(etopo["bathymetry"], z), "Unexpected value"


def test_bathymetry_greenwich():
    """Check elevation that includes 0
    """
    coords = [[0, 0, 4876], [6, 0, -76], [-10, 0, 5454]]
    for lat, lon, z in coords:
        etopo = get_bathymetry(lat, lon, resolution="5min")
        assert "bathymetry" in etopo, "Missing bathymetry from get_bathymetry"
        assert ma.allclose(etopo["bathymetry"], [z]), \
                "For ({},{}) expected {}".format(lat, lon, z)


def test_attribute():
    data = DummyData()

    coords = [[10, -30, 1], [10, 330, 1]]
    for lat, lon, flag in coords:
        data.attrs['LATITUDE'] = lat
        data.attrs['LONGITUDE'] = lon
        assert location_at_sea(data) == flag


def test_attribute_inland():
    data = DummyData()

    coords = [[-10, -60, 3], [-10, 300, 3]]
    for lat, lon, flag in coords:
        data.attrs['LATITUDE'] = lat
        data.attrs['LONGITUDE'] = lon
        assert location_at_sea(data) == flag


def notready_test_data():
    data = DummyData()

    data.data['LATITUDE'] = 10
    data.data['LONGITUDE'] = -30
    flag = location_at_sea(data)
    assert flag == 1

    data.data['LATITUDE'] = 10
    data.data['LONGITUDE'] = 330
    flag = location_at_sea(data)
    assert flag == 1


def test_badlocation():
    data = DummyData()

    coords = [[91, -30, 3], [-91, -30, 3], [10, -361, 3], [10, 1000, 3]]
    for lat, lon, flag in coords:
        data.attrs['LATITUDE'] = lat
        data.attrs['LONGITUDE'] = lon
        assert location_at_sea(data) == flag


def test_nonelocation():
    data = DummyData()

    coords = [[None, 1, 0], [1, None, 0]]
    for lat, lon, flag in coords:
        data.attrs['LATITUDE'] = lat
        data.attrs['LONGITUDE'] = lon
        assert location_at_sea(data) == flag

    del(data.attrs['LATITUDE'])
    data.attrs['LONGITUDE'] = 1
    assert location_at_sea(data) == 0

    del(data.attrs['LONGITUDE'])
    data.attrs['LATITUDE'] = 1
    assert location_at_sea(data) == 0


def test_LocationAtSea_attrs():
    """Test standard with single location

       Lat & Lon defined in the attrs

       Locking etopo resolution, since it can change the values.
    """
    data = DummyData()
    y = LocationAtSea(data, cfg={'resolution': '5min'})

    assert hasattr(y, 'features')
    assert 'bathymetry' in y.features
    assert ma.allclose(y.features['bathymetry'], 5036)
    assert hasattr(y, 'flags')
    assert 'location_at_sea' in y.flags
    assert ma.allclose(y.flags['location_at_sea'], 1)


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
    data = DummyData()
    data.data['LATITUDE'] = [15, 12, 8]
    data.data['LONGITUDE'] = [-38, 222, 0]

    y = LocationAtSea(data, cfg={'resolution': '5min'})

    assert hasattr(y, 'features')
    assert 'bathymetry' in y.features
    assert ma.allclose(y.features['bathymetry'], [5036, 4995, -122])
    assert hasattr(y, 'flags')
    assert 'location_at_sea' in y.flags
    assert ma.allclose(y.flags['location_at_sea'], [1, 1, 4])
