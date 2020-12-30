# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
"""

from datetime import datetime
import numpy as np
from numpy import ma

from cotede.qctests import WOA_NormBias, woa_normbias
from cotede.qc import ProfileQC
from ..data import DummyData


def test_woa_normbias():
    profile = DummyData()
    features = woa_normbias(profile, "TEMP")

    for v in [
        "woa_mean",
        "woa_std",
        "woa_nsamples",
        "woa_se",
        "woa_bias",
        "woa_normbias",
    ]:
        assert v in features


def test_standard_dataset():
    """Test WOA_NormBias with a standard dataset
    """
    flags = {
        "woa_normbias": np.array(
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 9], dtype="i1"
        )
    }

    profile = DummyData()
    cfg = {"threshold": 3}
    y = WOA_NormBias(profile, "TEMP", cfg, autoflag=True)

    assert len(y.features) > 0
    for f in y.flags:
        assert np.allclose(y.flags[f], flags[f], equal_nan=True)


def test_features_non_masked_array():
    """WOA_NormBias should return features type array

    Originally I used masked arrays, which is the standard for OceansDB but
    recently I moved to regular arrays using NaN.
    """
    profile = DummyData()
    cfg = {"threshold": 3}
    y = WOA_NormBias(profile, "TEMP", cfg, autoflag=True)

    assert len(y.features) > 0
    for v in y.features:
        assert not isinstance(y.features[v], ma.MaskedArray)


def test_basic():
    """
    """
    profile = DummyData()
    cfg = {
        "TEMP": {"woa_normbias": {"threshold": 3, "flag_bad": 3}},
        "PSAL": {"woa_normbias": {"threshold": 3, "flag_bad": 3}},
    }
    pqc = ProfileQC(profile, cfg=cfg)

    assert "woa_normbias" in pqc.flags["TEMP"]
    assert sorted(np.unique(pqc.flags["TEMP"]["woa_normbias"])) == [1, 3, 9]
    assert sorted(np.unique(pqc.flags["PSAL"]["woa_normbias"])) == [1, 9]


def test_attribute():
    profile = DummyData()

    cfg = {"TEMP": {"woa_normbias": {"threshold": 3}}}
    pqc = ProfileQC(profile, cfg=cfg)
    assert "woa_normbias" in pqc.flags["TEMP"]
    assert pqc.flags["TEMP"]["woa_normbias"].shape == profile.data["TEMP"].shape
    assert np.unique(pqc.features["TEMP"]["woa_mean"]).size > 1
    assert np.allclose(
        pqc.flags["TEMP"]["woa_normbias"],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 9],
        equal_nan=True,
    )


def test_track():
    profile = DummyData()
    N = profile["TEMP"].size
    profile.data["LATITUDE"] = np.linspace(4, 25, N)
    profile.data["LONGITUDE"] = np.linspace(-30, -38, N)
    profile.data["PRES"] *= 0
    # Location in data, one per measurement, has precedence on attrs
    profile.attrs["LATITUDE"] = None
    profile.attrs["LONGITUDE"] = None

    cfg = {"TEMP": {"woa_normbias": {"threshold": 3}}}
    pqc = ProfileQC(profile, cfg=cfg)
    assert "woa_normbias" in pqc.flags["TEMP"]
    assert pqc.flags["TEMP"]["woa_normbias"].shape == profile.data["TEMP"].shape
    assert np.unique(pqc.features["TEMP"]["woa_mean"]).size > 1
    assert np.allclose(
        pqc.flags["TEMP"]["woa_normbias"],
        [1, 1, 1, 1, 1, 1, 3, 3, 3, 3, 3, 3, 3, 3, 9],
        equal_nan=True,
    )


def test_standard_error():
    """I need to improve this!!
    """

    profile = DummyData()
    profile.attrs["datetime"] = datetime(2016, 6, 4)
    profile.attrs["LATITUDE"] = -30.0
    profile.attrs["LONGITUDE"] = 15
    profile.data["PRES"] = np.array([2.0, 5.0, 6.0, 21.0, 44.0, 79.0, 1000, 5000])
    profile.data["TEMP"] = np.array([16.0, 15.6, 15.9, 15.7, 15.2, 14.1, 8.6, 2.0])

    cfg = {"TEMP": {"woa_normbias": {"threshold": 10}}}
    pqc = ProfileQC(profile, cfg=cfg)
    assert "woa_normbias" in pqc.flags["TEMP"]
    assert pqc.flags["TEMP"]["woa_normbias"].shape == profile.data["TEMP"].shape
    assert (pqc.flags["TEMP"]["woa_normbias"] == [1, 1, 1, 1, 1, 1, 3, 0]).all()

    cfg = {"TEMP": {"woa_normbias": {"threshold": 10, "use_standard_error": False}}}
    pqc_noSE = ProfileQC(profile, cfg=cfg)
    assert "woa_normbias" in pqc.flags["TEMP"]
    assert pqc.flags["TEMP"]["woa_normbias"].shape == profile.data["TEMP"].shape
    assert (pqc.flags["TEMP"]["woa_normbias"] == [1, 1, 1, 1, 1, 1, 3, 0]).all()

    cfg = {"TEMP": {"woa_normbias": {"threshold": 10, "use_standard_error": True}}}
    pqc_SE = ProfileQC(profile, cfg=cfg)
    assert "woa_normbias" in pqc.flags["TEMP"]
    assert pqc.flags["TEMP"]["woa_normbias"].shape == profile.data["TEMP"].shape
    assert (pqc.flags["TEMP"]["woa_normbias"] == [1, 1, 1, 1, 1, 1, 3, 0]).all()
