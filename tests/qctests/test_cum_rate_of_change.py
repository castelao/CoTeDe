#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Check cummulative Rate of Change QC test
"""

from numpy import ma

from cotede.qctests import cum_rate_of_change


def test():
    dummy_data = {
        'PRES': ma.masked_array([0.0, 100, 5000]),
        'TEMP': ma.masked_array([25.16, 19.73, 2.13]),
        'PSAL': ma.masked_array([36.00, 34.74, 34.66])
        }
    dummy_output = ma.masked_array([0, 5.43, 17.6],
            mask=[True, False, False])

    cfg = {
            'memory': 0.8,
            'threshold': None,
            'flag_good': 1,
            'flag_bad': 4
            }

    x = cum_rate_of_change(dummy_data, 'TEMP', cfg['memory'])

    assert type(x) is ma.MaskedArray
    assert (x == dummy_output).all()
