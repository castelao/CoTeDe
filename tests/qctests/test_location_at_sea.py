#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

#from numpy import ma

from cotede.qctests import location_at_sea

class DummyData(object):
    def __init__(self):
        self.attributes = {}
        self.data = {}
    def __getitem__(self, key):
        return data[key]

def test_attribute():
    data = DummyData()

    data.attributes['LATITUDE'] = 10
    data.attributes['LONGITUDE'] = -30
    flag = location_at_sea(data)
    assert flag == 1

    data.attributes['LATITUDE'] = 10
    data.attributes['LONGITUDE'] = 330
    flag = location_at_sea(data)
    assert flag == 1

def test_attribute_inland():
    data = DummyData()

    data.attributes['LATITUDE'] = -10
    data.attributes['LONGITUDE'] = -60
    flag = location_at_sea(data)
    assert flag == 3

    data.attributes['LATITUDE'] = -10
    data.attributes['LONGITUDE'] = 300
    flag = location_at_sea(data)
    assert flag == 3

def notreadytest_greenwich():
    data = DummyData()

    data.attributes['LATITUDE'] = 0
    data.attributes['LONGITUDE'] = 0
    flag = location_at_sea(data)
    assert flag == 3

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
