# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
"""

from datetime import datetime
import numpy as np

from cotede.qctests import woa_normbias
from cotede.qc import ProfileQC
from data import DummyData


def test():
    """
    """
    profile = DummyData()
    cfg = {"TEMP": {"woa_normbias": {"threshold": 10}},
            "PSAL": {"woa_normbias": {"threshold": 10}}}
    pqc = ProfileQC(profile, cfg=cfg)

    assert 'woa_normbias' in pqc.flags['TEMP']
    assert sorted(np.unique(pqc.flags['TEMP']['woa_normbias'])) == [1, 9]
    #assert sorted(np.unique(pqc.flags['TEMP2']['woa_normbias'])) == [1]
    assert sorted(np.unique(pqc.flags['PSAL']['woa_normbias'])) == [1, 9]
    #assert sorted(np.unique(pqc.flags['PSAL2']['woa_normbias'])) == [1]


def test_attribute():
    profile = DummyData()
    profile.attributes['datetime'] = datetime(2016,6,4)
    profile.attributes['LATITUDE'] = -30.0
    profile.attributes['LONGITUDE'] = 15
    profile.data['PRES'] = np.array([2.0, 5.0, 6.0, 21.0, 44.0, 79.0, 1000, 5000])
    profile.data['TEMP'] = np.array([16.0, 15.6, 15.9, 15.7, 15.2, 14.1, 8.6, 2.0])

    cfg = {"TEMP": {"woa_normbias": {"threshold": 10}}}
    pqc = ProfileQC(profile, cfg=cfg)
    assert 'woa_normbias' in pqc.flags['TEMP']
    assert pqc.flags['TEMP']['woa_normbias'].shape == profile.data['TEMP'].shape
    assert (pqc.flags['TEMP']['woa_normbias'] == [1, 1, 1, 1, 1, 1, 3, 0]).all()


def test_standard_error():
    """I need to improve this!!
    """

    profile = DummyData()
    profile.attributes['datetime'] = datetime(2016,6,4)
    profile.attributes['LATITUDE'] = -30.0
    profile.attributes['LONGITUDE'] = 15
    profile.data['PRES'] = np.array([2.0, 5.0, 6.0, 21.0, 44.0, 79.0, 1000, 5000])
    profile.data['TEMP'] = np.array([16.0, 15.6, 15.9, 15.7, 15.2, 14.1, 8.6, 2.0])

    cfg = {"TEMP": {"woa_normbias": {"threshold": 10}}}
    pqc = ProfileQC(profile, cfg=cfg)
    assert 'woa_normbias' in pqc.flags['TEMP']
    assert pqc.flags['TEMP']['woa_normbias'].shape == profile.data['TEMP'].shape
    assert (pqc.flags['TEMP']['woa_normbias'] == [1, 1, 1, 1, 1, 1, 3, 0]).all()

    cfg = {"TEMP": {"woa_normbias": {
        "threshold": 10, "use_standard_error": False}}}
    pqc_noSE = ProfileQC(profile, cfg=cfg)
    assert 'woa_normbias' in pqc.flags['TEMP']
    assert pqc.flags['TEMP']['woa_normbias'].shape == profile.data['TEMP'].shape
    assert (pqc.flags['TEMP']['woa_normbias'] == [1, 1, 1, 1, 1, 1, 3, 0]).all()

    cfg = {"TEMP": {"woa_normbias": {"threshold": 10, "use_standard_error": True}}}
    pqc_SE = ProfileQC(profile, cfg=cfg)
    assert 'woa_normbias' in pqc.flags['TEMP']
    assert pqc.flags['TEMP']['woa_normbias'].shape == profile.data['TEMP'].shape
    assert (pqc.flags['TEMP']['woa_normbias'] == [1, 1, 1, 1, 1, 1, 3, 0]).all()
