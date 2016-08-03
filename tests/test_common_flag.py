#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

import numpy as np
from cotede.qc import ProfileQC

class DummyData(object):
    def __init__(self):
        self.attributes = {'LATITUDE': 15, 'LONGITUDE': -38}
        self.data = {'TEMP': np.array([1,2,3])}
    def __getitem__(self, key):
        return self.data[key]
    def keys(self):
        return self.data.keys()

def test_common_flags():
    profile = DummyData()
    cfg = {"main": {"valid_datetime": None, "valid_geolocation": None},
            "TEMP": {}}
    pqc = ProfileQC(profile, cfg=cfg)

    assert 'common' in pqc.flags
    assert 'valid_datetime' in pqc.flags['TEMP']
    assert pqc.flags['TEMP']['valid_datetime'].shape == profile['TEMP'].shape




