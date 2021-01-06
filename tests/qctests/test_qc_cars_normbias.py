# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
"""

from datetime import datetime
import numpy as np

from cotede.qctests import CARS_NormBias, cars_normbias
from cotede.qc import ProfileQC
from ..data import DummyData


def test_cars_normbias_standard_dataset():
    profile = DummyData()
    features = cars_normbias(profile, "TEMP")

    for v in [
        "cars_mean",
        "cars_std",
        # "cars_nsamples",
        "cars_bias",
        "cars_normbias",
    ]:
        assert v in features


def test_cars_normbias_invalid_position():
    profile = DummyData()
    assert "LONGITUDE" in profile.attrs
    profile.attrs["LONGITUDE"] = 38
    features = cars_normbias(profile, "TEMP")
    for v in [
        "cars_mean",
        "cars_std",
        # "cars_nsamples",
        "cars_bias",
        "cars_normbias",
    ]:
        assert np.isnan(features[v]).all()


def test_standard_dataset():
    """Test CARS_NormBias with a standard dataset
    """
    flags = {
        "cars_normbias": np.array(
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 9], dtype="i1"
        )
    }

    profile = DummyData()
    cfg = {"threshold": 3}
    y = CARS_NormBias(profile, "TEMP", cfg, autoflag=True)

    assert len(y.features) > 0
    for f in y.flags:
        assert np.allclose(y.flags[f], flags[f], equal_nan=True)


def test():
    """
    """
    profile = DummyData()
    cfg = {
        "TEMP": {"cars_normbias": {"threshold": 10}},
        "PSAL": {"cars_normbias": {"threshold": 10}},
    }
    pqc = ProfileQC(profile, cfg=cfg)

    assert "cars_normbias" in pqc.flags["TEMP"]
    assert sorted(np.unique(pqc.flags["TEMP"]["cars_normbias"])) == [1, 9]
    # assert sorted(np.unique(pqc.flags['TEMP2']['cars_normbias'])) == [1]
    assert sorted(np.unique(pqc.flags["PSAL"]["cars_normbias"])) == [1, 9]
    # assert sorted(np.unique(pqc.flags['PSAL2']['cars_normbias'])) == [1]


def test_attribute():
    profile = DummyData()
    profile.attrs["datetime"] = datetime(2016, 6, 4)
    profile.attrs["LATITUDE"] = -30.0
    profile.attrs["LONGITUDE"] = 15
    profile.data["PRES"] = np.array([2.0, 5.0, 6.0, 21.0, 44.0, 79.0])
    profile.data["TEMP"] = np.array([16.0, 15.6, 15.9, 5.7, 15.2, 14.1])

    cfg = {"TEMP": {"cars_normbias": {"threshold": 6}}}
    pqc = ProfileQC(profile, cfg=cfg)
    assert "cars_normbias" in pqc.flags["TEMP"]
    assert pqc.flags["TEMP"]["cars_normbias"].shape == profile.data["TEMP"].shape
    assert (pqc.flags["TEMP"]["cars_normbias"] == [1, 1, 1, 3, 1, 1]).all()


def test_standard_error():
    """I need to improve this!!
    """

    profile = DummyData()
    profile.attrs["datetime"] = datetime(2016, 6, 4)
    profile.attrs["LATITUDE"] = -30.0
    profile.attrs["LONGITUDE"] = 15
    profile.data["PRES"] = np.array([2.0, 5.0, 6.0, 21.0, 44.0, 79.0])
    profile.data["TEMP"] = np.array([16.0, 15.6, 15.9, 5.7, 15.2, 14.1])

    cfg = {"TEMP": {"cars_normbias": {"threshold": 6}}}
    pqc = ProfileQC(profile, cfg=cfg)
    assert "cars_normbias" in pqc.flags["TEMP"]
    assert pqc.flags["TEMP"]["cars_normbias"].shape == profile.data["TEMP"].shape
    assert (pqc.flags["TEMP"]["cars_normbias"] == [1, 1, 1, 3, 1, 1]).all()

    cfg = {"TEMP": {"cars_normbias": {"threshold": 6, "use_standard_error": False}}}
    pqc_noSE = ProfileQC(profile, cfg=cfg)
    assert "cars_normbias" in pqc.flags["TEMP"]
    assert pqc.flags["TEMP"]["cars_normbias"].shape == profile.data["TEMP"].shape
    assert (pqc.flags["TEMP"]["cars_normbias"] == [1, 1, 1, 3, 1, 1]).all()

    # cfg = {"TEMP": {"cars_normbias": {"threshold": 6, "use_standard_error": True}}}
    # pqc_SE = ProfileQC(profile, cfg=cfg)
    # assert 'cars_normbias' in pqc.flags['TEMP']
    # assert pqc.flags['TEMP']['cars_normbias'].shape == profile.data['TEMP'].shape
    # assert (pqc.flags['TEMP']['cars_normbias'] == [1, 1, 1, 1, 1, 1, 3, 0]).all()
