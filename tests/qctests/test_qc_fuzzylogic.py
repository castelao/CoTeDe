# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

""" Check Fuzzy Logic QC test
"""

import numpy as np
from numpy import ma

from cotede.qc import ProfileQC
from data import DummyData


def test():
    """
    """
    profile = DummyData()

    pqc = ProfileQC(profile, cfg='fuzzylogic')

    assert 'fuzzylogic' in pqc.flags['TEMP']
    assert 'fuzzylogic' in pqc.flags['PSAL']

    assert profile['TEMP'].shape == pqc.flags['TEMP']['fuzzylogic'].shape
    assert profile['PSAL'].shape == pqc.flags['PSAL']['fuzzylogic'].shape

    # assert sorted(np.unique(pqc.flags['TEMP']['fuzzylogic'])) == [0, 1, 3]
    # assert sorted(np.unique(pqc.flags['TEMP2']['fuzzylogic'])) == [1]
    # assert sorted(np.unique(pqc.flags['PSAL']['fuzzylogic'])) == [0, 1]
    # assert sorted(np.unique(pqc.flags['PSAL2']['fuzzylogic'])) == [1]
