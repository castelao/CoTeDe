#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Check morello2014 test
"""

import numpy as np

from cotede.qc import ProfileQC
from data import DummyData

def test():
    """
    """
    profile = DummyData()

    pqc = ProfileQC(profile, cfg='morello2014')

    assert 'morello2014' in pqc.flags['TEMP']
    assert 'morello2014' in pqc.flags['PSAL']

    assert profile['TEMP'].shape == pqc.flags['TEMP']['morello2014'].shape
    assert profile['PSAL'].shape == pqc.flags['PSAL']['morello2014'].shape

    # assert sorted(np.unique(pqc.flags['TEMP']['morello2014'])) == [1, 2, 3, 4]
    # assert sorted(np.unique(pqc.flags['TEMP2']['morello2014'])) == [1]
    # assert sorted(np.unique(pqc.flags['PSAL']['morello2014'])) == [1, 2, 4]
    # assert sorted(np.unique(pqc.flags['PSAL2']['morello2014'])) == [1]
