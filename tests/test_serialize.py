#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Check if pickle can serialize CoTeDe's dataset.

This is critical to allow running CoTeDe with multiprocessing.
"""

import pickle

import numpy as np

from cotede.qc import ProfileQC
from .data import DummyData


def test_serialize_ProfileQC():
    """Serialize ProfileQC

    Guarantee that the returned object can be processed by pickle, thus it
    can be transported in queues.
    """
    profile = DummyData()
    pqc = ProfileQC(profile)
    pqc2 = pickle.loads(pickle.dumps(pqc))

    assert sorted(pqc.data.keys()) == sorted(pqc2.data.keys())
    for v in pqc.data:
        assert np.allclose(pqc[v], pqc2[v], equal_nan=True)

    assert sorted(pqc.attributes.keys()) == sorted(pqc2.attributes.keys())
    for v in pqc.attributes:
        assert pqc.attributes[v] == pqc2.attributes[v]

    assert sorted(pqc.flags.keys()) == sorted(pqc2.flags.keys())
    for v in pqc.flags:
        for f in pqc.flags[v]:
            assert np.allclose(pqc.flags[v][f], pqc2.flags[v][f])
