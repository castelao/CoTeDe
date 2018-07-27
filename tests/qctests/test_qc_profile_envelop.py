# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
"""

import numpy as np
from numpy import ma

from cotede.qctests import profile_envelop
from data import DummyData


def test():
    profile = DummyData()

    cfg = [
        ["> 0", "<= 25", -2, 37],
        ["> 25", "<= 50", -2, 36]]

    flags = profile_envelop(profile, cfg, 'TEMP')

    # Check for BUG #9.
    assert 9 in flags
