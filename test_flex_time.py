# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""

Missing tests:
- validate explicitly giver time varname
- check for type of the output
- Does it work with timezone?
"""

import numpy as np
# from .data import DummyData
from data import DummyData
try:
    from cotede.utils import extract_time
except:
    pass


def test_import():
    """Check if extract_time is available at the same place

    I might change the place of extract_time in the future, so verify
    if it is where I expected.
    """
    from cotede.utils import extract_time


def test_standard_dataset():
    profile = DummyData()

    t = extract_time(profile)
    assert np.datetime64(t) == np.datetime64("2016-06-04")


def test_timeseries():
    alongtrack = {
        "time": ["2000-01-01", "2000-01-02", "2000-01-03"],
        "DEPTH": [0, 0, 0],
        "latitude": [11.9, 12, 12.1],
        "longitude": [38, 38.1, 38],
    }
    t = extract_time(alongtrack)
    assert np.array_equal(t, np.array(alongtrack['time']).astype("datetime64[s]"))
