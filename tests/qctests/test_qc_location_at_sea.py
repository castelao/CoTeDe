#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Consistency check for location at sea QC test.
"""

from cotede.qctests import location_at_sea


class DummyData(object):
    def __init__(self):
        self.attributes = {}
        self.data = {}
    def __getitem__(self, key):
        return data[key]


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

    coords = [[91, -30, 0], [-91, -30, 0], [10, -361, 0], [10, 1000, 0]]
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
