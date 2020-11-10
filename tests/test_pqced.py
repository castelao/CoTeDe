# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

""" Check ProfileQCed
"""

import numpy as np

from cotede.qc import ProfileQC, ProfileQCed
from ..data import DummyData


def test():
    """
    """
    profile = DummyData()
    pqc = ProfileQC(profile)

    pqced = ProfileQCed(profile)

    assert pqc.data.keys() == pqced.data.keys()
    for v in pqc.data:
        assert np.allclose(pqc[v].data, pqced[v].data, equal_nan=True)

    assert not np.allclose(pqc["TEMP"].mask, pqced["TEMP"].mask)

    assert pqc.attributes.keys() == pqced.attributes.keys()
    for v in pqc.attributes:
        assert pqc.attributes[v] == pqced.attributes[v]

    assert pqc.flags.keys() == pqced.flags.keys()
    for v in pqc.flags:
        for f in pqc.flags[v]:
            assert np.allclose(pqc.flags[v][f], pqced.flags[v][f]), "Didn't match {}, {}".format(v, f)
