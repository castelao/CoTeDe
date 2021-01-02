# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""

Missing tests:
- validate explicitly giver time varname
- check for type of the output
- Does it work with timezone?
"""

from datetime import datetime

import numpy as np

from .data import DummyData

try:
    from cotede.utils import extract_time, day_of_year
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
    assert np.array_equal(t, np.array(alongtrack["time"]).astype("datetime64[s]"))


def test_day_of_year_with_time():
    """Operate in days even if time (H:M:S) are given
    """
    doy = day_of_year("2000-01-01T00:00:00")
    assert doy == 1

    doy = day_of_year(["2000-01-01T00:00:00", "2000-01-02T00:00:00"])
    assert np.array_equal(doy, [1, 2])


def test_get_doy_single_datetime():
    doy = day_of_year(datetime(2000, 1, 1))
    assert doy == 1


def test_get_doy_sequence_datetime():
    time = (datetime(2000, 1, 1), datetime(2001, 1, 1))

    doy = day_of_year(time)
    assert np.array_equal(doy, [1, 1])

    doy = day_of_year(list(time))
    assert np.array_equal(doy, [1, 1])


def test_get_doy_single_datetime64():
    doy = day_of_year(np.datetime64("2000-01-01"))
    assert doy == 1


def test_get_doy_sequence_datetime64():
    time = (np.datetime64("2000-01-01"), np.datetime64("2001-01-01"))

    doy = day_of_year(time)
    assert np.array_equal(doy, [1, 1])

    doy = day_of_year(list(time))
    assert np.array_equal(doy, [1, 1])

    doy = day_of_year(np.array(time))
    assert np.array_equal(doy, [1, 1])
