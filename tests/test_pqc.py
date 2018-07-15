# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

""" Check fundamentals of ProfileQC object
"""

# I should split in two tests, one for generic expected proprieties and
#   contents, and another test for specific contents, like keys, and values
#   itself. But this last one must require a md5.


import numpy as np

import cotede.qc
from cotede.qc import ProfileQC
from cotede.misc import combined_flag
from data import DummyData


def test():
    profile = DummyData()

    pqc = ProfileQC(profile, saveauxiliary=False)
    pqc = ProfileQC(profile, saveauxiliary=True)


    keys = ['PRES', 'TEMP', 'PSAL', 'flag']
    for v in profile.keys():
        assert v in pqc.keys()
        assert np.allclose(profile[v], pqc[v])

    for a in profile.attributes:
        assert a in pqc.attributes
        assert profile.attributes[a] == pqc.attributes[a]

    assert hasattr(pqc, 'flags')
    assert type(pqc.flags) is dict
    vs = list(pqc.flags.keys())
    vs.remove('common')
    for v in vs:
        for f in pqc.flags[v]:
            assert pqc.flags[v][f].dtype == 'i1'

    assert hasattr(pqc, 'features')
    assert type(pqc.features) is dict


def test_all_valid_no_9():
    """ If all measurements are valid it can't return flag 9

        This is to test a special condition when all values are valid, .mask
          return False, instead of an array on the same size with False.

        This test input all valid values, and check if there is no flag 9.
    """
    profile = DummyData()

    pqc = ProfileQC(profile)

    assert pqc['TEMP'].mask.all() == False
    assert np.allclose(combined_flag(pqc.flags['TEMP']) == 9,
                       profile['TEMP'].mask)
