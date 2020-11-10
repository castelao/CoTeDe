# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

""" Check anomaly detection QC test
"""

import numpy as np

from cotede.qc import ProfileQC
from ..data import DummyData


def test():
    """ Only test if run. Must improve this.
    """
    profile = DummyData()

    pqc = ProfileQC(profile, cfg='anomaly_detection')

    assert 'anomaly_detection' in pqc.flags['TEMP']
    assert 'anomaly_detection' in pqc.flags['PSAL']

    assert profile['TEMP'].shape == pqc.flags['TEMP']['anomaly_detection'].shape
    assert profile['PSAL'].shape == pqc.flags['PSAL']['anomaly_detection'].shape

    # While anomaly detection is limited to spike, gradient and tukey tests it
    #   will always return 0 for the first and last.
    # assert sorted(np.unique(pqc.flags['TEMP']['anomaly_detection'])) == [1,4]
