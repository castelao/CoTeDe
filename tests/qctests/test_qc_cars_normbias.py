#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

#from numpy import ma

from datetime import datetime
import numpy as np
from cotede.qctests import cars_normbias
from cotede.qc import ProfileQC
from data import DummyData


def test_attribute():
    profile = DummyData()
    profile.attributes['datetime'] = datetime(2016, 6, 4)
    profile.attributes['LATITUDE'] = -30.0
    profile.attributes['LONGITUDE'] = 15
    profile.data['PRES'] = np.array([2.0, 5.0, 6.0, 21.0, 44.0, 79.0, 1000, 5000])
    profile.data['TEMP'] = np.array([16.0, 15.6, 15.9, 5.7, 15.2, 14.1, 8.6, 2.0])

    cfg = {"TEMP": {"cars_normbias": {"threshold": 6}}}
    pqc = ProfileQC(profile, cfg=cfg)
    print(pqc.features['TEMP'])
    assert 'cars_normbias' in pqc.flags['TEMP']
    assert pqc.flags['TEMP']['cars_normbias'].shape == profile.data['TEMP'].shape
    assert (pqc.flags['TEMP']['cars_normbias'] == [1, 1, 1, 3, 1, 1, 0, 0]).all()


def test_standard_error():
    """I need to improve this!!
    """

    profile = DummyData()
    profile.attributes['datetime'] = datetime(2016, 6, 4)
    profile.attributes['LATITUDE'] = -30.0
    profile.attributes['LONGITUDE'] = 15
    profile.data['PRES'] = np.array([2.0, 5.0, 6.0, 21.0, 44.0, 79.0, 1000, 5000])
    profile.data['TEMP'] = np.array([16.0, 15.6, 15.9, 5.7, 15.2, 14.1, 8.6, 2.0])

    cfg = {"TEMP": {"cars_normbias": {"threshold": 6}}}
    pqc = ProfileQC(profile, cfg=cfg)
    assert 'cars_normbias' in pqc.flags['TEMP']
    assert pqc.flags['TEMP']['cars_normbias'].shape == profile.data['TEMP'].shape
    assert (pqc.flags['TEMP']['cars_normbias'] == [1, 1, 1, 3, 1, 1, 0, 0]).all()

    cfg = {"TEMP": {"cars_normbias": {
        "threshold": 6, "use_standard_error": False}}}
    pqc_noSE = ProfileQC(profile, cfg=cfg)
    assert 'cars_normbias' in pqc.flags['TEMP']
    assert pqc.flags['TEMP']['cars_normbias'].shape == profile.data['TEMP'].shape
    assert (pqc.flags['TEMP']['cars_normbias'] == [1, 1, 1, 3, 1, 1, 0, 0]).all()

    #cfg = {"TEMP": {"cars_normbias": {"threshold": 6, "use_standard_error": True}}}
    #pqc_SE = ProfileQC(profile, cfg=cfg)
    #assert 'cars_normbias' in pqc.flags['TEMP']
    #assert pqc.flags['TEMP']['cars_normbias'].shape == profile.data['TEMP'].shape
    #assert (pqc.flags['TEMP']['cars_normbias'] == [1, 1, 1, 1, 1, 1, 3, 0]).all()
