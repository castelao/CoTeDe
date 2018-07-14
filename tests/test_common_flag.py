# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
"""

import numpy as np
from cotede.qc import ProfileQC

from data import DummyData


def test_common_flags():
    profile = DummyData()

    cfg = {"main": {"valid_datetime": None, "valid_geolocation": None},
            "TEMP": {}}
    pqc = ProfileQC(profile, cfg=cfg)

    assert 'common' in pqc.flags
    assert 'valid_datetime' in pqc.flags['TEMP']
    assert pqc.flags['TEMP']['valid_datetime'].shape == profile['TEMP'].shape
