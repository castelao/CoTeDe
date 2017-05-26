#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Check density inversion QC test
"""

from numpy import ma

from cotede.qctests import density_inversion


def test():
    try:
        import gsw
    except:
        print('GSW package not available. Can\'t run density_inversion test.')
        return

    dummy_data = {
        'PRES': ma.masked_array([0.0, 100, 5000]),
        'TEMP': ma.masked_array([25.18, 19.73, 2.13]),
        'PSAL': ma.masked_array([36.00, 34.74, 34.66])
        }

    cfg = {
            'threshold': -0.03,
            'flag_good': 1,
            'flag_bad': 4
            }

    f, x = density_inversion(dummy_data, cfg, saveaux=True)

    assert (f == [0,4,4]).all()
