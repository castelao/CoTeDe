# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

""" Check special cases
"""


from datetime import datetime, date

from numpy import ma

from cotede.qc import ProfileQC
from .data import DummyData


def test_single_measurement():
    """Evaluate a profile with a single measurement

    WOD has some profiles with a single measurement. Something certainly went
    wrong on those profiles, despite that, CoTeDe should be able to do the
    best assessement possible. Some tests can't be applied, like spike which
    requires neighbor measurements, but those should return flag 0.
    """
    profile = DummyData()
    profile.attrs = {
        "id": 609483,
        "LATITUDE": 6.977,
        "LONGITUDE": 79.873,
        "datetime": datetime(2009, 8, 14, 1, 18, 36),
        "date": date(2009, 8, 14),
        "schema": "pfl",
    }

    profile.data = {
        "id": ma.masked_array(data=[51190527], mask=[False], dtype="i"),
        "PRES": ma.masked_array(data=[1.0], mask=[False], dtype="f"),
        "TEMP": ma.masked_array(data=[25.81], mask=[False], dtype="f"),
        "PSAL": ma.masked_array(data=[0.01], mask=[False], dtype="f"),
    }

    ProfileQC(profile, saveauxiliary=False)
    ProfileQC(profile, saveauxiliary=True)


def test_single_negative_depth():
    """Evaluate a profile with a single measurement

    WOD has some profiles with a single measurement. Something certainly went
    wrong on those profiles, despite that, CoTeDe should be able to do the
    best assessement possible. Some tests can't be applied, like spike which
    requires neighbor measurements, but those should return flag 0.
    """
    profile = DummyData()
    profile.attrs = {
        "id": 609483,
        "LATITUDE": 6.977,
        "LONGITUDE": 79.873,
        "datetime": datetime(2009, 8, 14, 1, 18, 36),
        "date": date(2009, 8, 14),
        "schema": "pfl",
    }

    profile.data = {
        "id": ma.masked_array(data=[51190527], mask=[False], dtype="i"),
        "PRES": ma.masked_array(data=[-1.0], mask=[False], dtype="f"),
        "TEMP": ma.masked_array(data=[25.81], mask=[False], dtype="f"),
        "PSAL": ma.masked_array(data=[0.01], mask=[False], dtype="f"),
    }

    ProfileQC(profile, saveauxiliary=False)
    ProfileQC(profile, saveauxiliary=True)
