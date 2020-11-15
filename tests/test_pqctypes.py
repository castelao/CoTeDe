# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

""" Check the structure of a ProfileQC object
"""

# I should split in two tests, one for generic expected proprieties and
#   contents, and another test for specific contents, like keys, and values
#   itself. But this last one must require a md5.

import numpy as np

from cotede.qc import ProfileQC
from .data import DummyData


def test():
    profile = DummyData()
    pqc = ProfileQC(profile)

    # assert type(pqc.keys()) == list
    assert type(pqc.attributes) == dict
    assert hasattr(pqc, 'input')
    assert hasattr(pqc, 'flags')
    assert hasattr(pqc, 'features')
    assert type(pqc.flags) == dict
    for k in pqc.flags.keys():
        assert type(pqc.flags[k]) == dict
        for kk in pqc.flags[k].keys():
            assert (type(pqc.flags[k][kk]) == np.ndarray) or \
                (type(pqc.flags[k][kk]) == int)
            if (type(pqc.flags[k][kk]) == np.ndarray):
                assert pqc.flags[k][kk].dtype == 'int8'
