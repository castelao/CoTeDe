#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Check cummulative Rate of Change QC test
"""

from numpy import ma
from cotede.qctests import CumRateOfChange, cum_rate_of_change
from data import DummyData


def test():
    profile = DummyData()

    dummy_output = ma.masked_array([0, 5.43, 4.93, 14.68],
            mask=[True, False, False, False])

    cfg = {
            'memory': 0.8,
            'threshold': 4,
            'flag_good': 1,
            'flag_bad': 4
            }

    y = CumRateOfChange(profile, 'TEMP', cfg)
    assert type(y.features) is dict

    x = cum_rate_of_change(profile['TEMP'], cfg['memory'])
    assert type(x) is ma.MaskedArray
    # assert ma.allclose(x, dummy_output)
