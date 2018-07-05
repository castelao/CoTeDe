#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Check density inversion QC test
"""

from numpy import ma
from cotede.qctests import density_inversion
from data import DummyData


def test():
    try:
        import gsw
    except:
        print('GSW package not available. Can\'t run density_inversion test.')
        return

    profile = DummyData()
    profile.data['PRES'] = ma.masked_array([1.0, 100, 200, 300, 500, 5000])
    profile.data['TEMP'] = ma.masked_array([27.44, 14.55, 11.96, 11.02, 7.65, 2.12])
    profile.data['PSAL'] = ma.masked_array([35.71, 35.50, 35.13, 35.02, 34.72, 35.03])

    cfg = {
            'threshold': -0.03,
            'flag_good': 1,
            'flag_bad': 4
            }

    f, x = density_inversion(profile, cfg, saveaux=True)

    assert (f == [0, 4, 4, 4, 4, 4]).all()
