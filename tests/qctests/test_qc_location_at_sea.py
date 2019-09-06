#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Consistency check for location at sea QC test.
"""

from cotede.qctests import LocationAtSea, location_at_sea
from data import DummyData


def test_attribute():
    data = DummyData()

    coords = [[10, -30, 1], [10, 330, 1]]
    for lat, lon, flag in coords:
        data.attributes['LATITUDE'] = lat
        data.attributes['LONGITUDE'] = lon
        assert location_at_sea(data) == flag


def test_attribute_inland():
    data = DummyData()

    coords = [[-10, -60, 3], [-10, 300, 3]]
    for lat, lon, flag in coords:
        data.attributes['LATITUDE'] = lat
        data.attributes['LONGITUDE'] = lon
        assert location_at_sea(data) == flag


def test_greenwich():
    data = DummyData()

    coords = [[0, 0, 1], [6, 0, 3], [-10, 0, 1]]
    for lat, lon, flag in coords:
        data.attributes['LATITUDE'] = lat
        data.attributes['LONGITUDE'] = lon
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
        data.attributes['LATITUDE'] = lat
        data.attributes['LONGITUDE'] = lon
        assert location_at_sea(data) == flag


def test_nonelocation():
    data = DummyData()

    coords = [[None, 1, 0], [1, None, 0]]
    for lat, lon, flag in coords:
        data.attributes['LATITUDE'] = lat
        data.attributes['LONGITUDE'] = lon
        assert location_at_sea(data) == flag

    del(data.attributes['LATITUDE'])
    data.attributes['LONGITUDE'] = 1
    assert location_at_sea(data) == 0

    del(data.attributes['LONGITUDE'])
    data.attributes['LATITUDE'] = 1
    assert location_at_sea(data) == 0


def test_LocationAtSea():
    data = DummyData()
    t = LocationAtSea(data, cfg={})
    assert hasattr(t, 'features')
    assert 'bathymetry' in t.features
    assert hasattr(t, 'flags')
    assert 'location_at_sea' in t.flags
