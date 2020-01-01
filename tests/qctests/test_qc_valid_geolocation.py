#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Consistency check for valid geolocation QC test.
"""

from cotede.qctests.valid_geolocation import *
from data import DummyData


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
    coords = [[10, -30, True], [10, 330, True], ]
    for lat, lon, flag in coords:
        assert valid_geolocation(lat, lon) == flag


def test_valid_coordinate():
    lat = [10, 10, -15]
    lon = [-30, 330, 30]
    flag = [True, True, True]
    assert np.all(valid_geolocation(lat, lon) == flag)


def test_ValidGeolocation():
    data = DummyData()
    y = ValidGeolocation(data, 'sea_water_temperature', cfg={})
    assert hasattr(y, 'features')
    assert hasattr(y, 'flags')

