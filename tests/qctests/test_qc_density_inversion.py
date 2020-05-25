#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Check density inversion QC test
"""

from numpy import ma
from cotede.qc import ProfileQC
from cotede.qctests import DensityInversion
from data import DummyData

try:
    import gsw

    nogsw = False
except ImportError:
    nogsw = True


def test():
    if nogsw:
        print("GSW package not available. Can't run density_inversion test.")
        return

    profile = DummyData()
    profile.data["PRES"] = ma.masked_array([1.0, 100, 200, 300, 500, 5000])
    profile.data["TEMP"] = ma.masked_array([27.44, 14.55, 11.96, 11.02, 7.65, 2.12])
    profile.data["PSAL"] = ma.masked_array([35.71, 35.50, 35.13, 35.02, 34.72, 35.03])

    cfg = {"threshold": -0.03, "flag_good": 1, "flag_bad": 4}

    y = DensityInversion(profile, cfg)

    assert type(y.features) is dict
    assert "densitystep" in y.features


def test_ProfileQC():
    if nogsw:
        print("GSW package not available. Can't run density_inversion test.")
        return

    profile = DummyData()
    profile["TEMP"][4] = profile["TEMP"][3] + 5

    cfg = {
        "TEMP": {
            "density_inversion": {"threshold": -0.03, "flag_good": 1, "flag_bad": 4}
        }
    }

    pqc = ProfileQC(profile, cfg)

    assert type(pqc.features) is dict
    assert "densitystep" in pqc.features["TEMP"]

    assert type(pqc.flags) is dict
    assert "density_inversion" in pqc.flags["TEMP"]
    assert pqc.flags["TEMP"]["density_inversion"][4] == 4
