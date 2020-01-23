# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
"""

import numpy as np
from numpy import ma

from cotede.qc import ProfileQC
from data import DummyData
from cotede.qctests import RegionalRange


def test_default():
    """Test Regional Range on the default DummyData

       Must recognize flags 1, 4, and 9.
    """
    profile = DummyData()
    cfg = {'name': 'PIRATA',
            'region': 'POLYGON ((-40 10, -40 20, -30 20, -30 10, -40 10))',
            'minval': 15.0,
            'maxval': 40
            }
    y = RegionalRange(profile, 'TEMP', cfg)

    assert 'regional_range' in y.flags
    assert profile['TEMP'].shape == y.flags['regional_range'].shape

    idx = ma.getmaskarray(profile['TEMP'])
    assert idx.any(), "Redefine cfg to have at least one masked value"
    try:
        import shapely
        assert np.all(y.flags['regional_range'][idx] == 9)
    except ImportError:
        # If Shapely is not available, return 0, i.e. no evaluation.
        assert np.all(y.flags['regional_range'][idx] == 0)
        return

    x = profile['TEMP'][y.flags['regional_range'] == 1]
    idx = (x >= cfg['minval']) & (x <= cfg['maxval'])
    assert idx.any(), "Redefine cfg to have at least one valid value"
    assert idx.all()
    x = profile['TEMP'][y.flags['regional_range'] == 4]
    idx = (x < cfg['minval']) | (x > cfg['maxval'])
    assert idx.any(), "Redefine cfg to have at least one non-valid value"
    assert idx.all()


def test_nolatlon():
    """If missing lat or lon, return flag 0 for everything
    """
    cfg = {'name': 'PIRATA',
            'region': 'POLYGON ((-40 10, -40 20, -30 20, -30 10, -40 10))',
            'minval': 2.0,
            'maxval': 40
            }

    profile = DummyData()
    del(profile.attrs['LATITUDE'])
    y = RegionalRange(profile, 'TEMP', cfg)
    assert 'regional_range' in y.flags
    flag = y.flags['regional_range']
    assert profile['TEMP'].shape == flag.shape
    assert (flag == 0).all()

    profile = DummyData()
    del(profile.attrs['LONGITUDE'])
    y = RegionalRange(profile, 'TEMP', cfg)
    assert 'regional_range' in y.flags
    flag = y.flags['regional_range']
    assert profile['TEMP'].shape == flag.shape
    assert (flag == 0).all()


def test_nocoverage():
    """Test when Regional Range does not cover the data position.

       Returns flag 9 for invalid measurements and 0 for everything else.
    """
    profile = DummyData()
    cfg = {'name': 'red_sea',
            'region': 'POLYGON ((10 40, 20 50, 30 30, 10 40))',
            'minval': 21.7,
            'maxval': 40
            }
    y = RegionalRange(profile, 'TEMP', cfg)

    assert 'regional_range' in y.flags
    assert profile['TEMP'].shape == y.flags['regional_range'].shape

    idx = ma.getmaskarray(profile['TEMP'])
    assert idx.any(), "Redefine cfg to have at least one masked value"
    try:
        import shapely
        assert np.all(y.flags['regional_range'][idx] == 9)
    except ImportError:
        # If Shapely is not available, return 0, i.e. no evaluation.
        assert np.all(y.flags['regional_range'][idx] == 0)
        return

    assert np.all(y.flags['regional_range'][~idx] == 0)
