#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Check density inversion QC test
"""

import numpy as np

from cotede.qc import ProfileQC
from cotede.qctests import DensityInversion, densitystep
from ..data import DummyData

from .compare import compare_feature_input_types, compare_input_types

try:
    import gsw

    GSW_AVAILABLE = True
except ImportError:
    GSW_AVAILABLE = False


def test_densitystep():
    if not GSW_AVAILABLE:
        return

    p = [1.0, 100, 200, 300, 500, 5000, np.nan]
    t = [27.44, 14.55, 11.96, 11.02, 7.65, 2.12, 2.12]
    s = [35.71, 35.50, 35.13, 35.02, 34.72, 35.03, 35.03]

    output = [np.nan, 3.3484632, 0.2433187, 0.0911988, 0.317172, 0.9046589, np.nan]

    drho = densitystep(s, t, p)

    assert isinstance(drho, np.ndarray)
    assert type(drho) == np.ndarray
    assert np.allclose(drho, output, equal_nan=True)


def test_feature_input_types():
    if not GSW_AVAILABLE:
        return

    p = [1.0, 100, 200, 300, 500, 5000, np.nan]
    t = [27.44, 14.55, 11.96, 11.02, 7.65, 2.12, 2.12]
    SA = [35.71, 35.50, 35.13, 35.02, 34.72, 35.03, 35.03]

    compare_feature_input_types(densitystep, SA=SA, t=t, p=p)


def test_standard_dataset():
    """Test DensityInversion procedure with a standard dataset
    """
    if not GSW_AVAILABLE:
        return

    profile = DummyData()

    features = {
        "densitystep": [
            np.nan,
            0.0091339,
            0.0077907,
            0.0175282,
            0.1450310,
            0.5896058,
            0.5023247,
            0.7156530,
            0.2924434,
            0.3559480,
            0.6476343,
            -0.4131068,
            0.2489996,
            np.nan,
            np.nan,
        ]
    }
    flags = {"density_inversion": [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1, 0, 0]}

    cfg = {"threshold": -0.03}

    y = DensityInversion(profile, cfg)

    for f in features:
        assert np.allclose(y.features[f], features[f], equal_nan=True)
    for f in flags:
        assert np.allclose(y.flags[f], flags[f], equal_nan=True)


def test_densityinversion_from_profileqc():
    """Validate if ProfileQC can run DensityInversion

    It requires GSW to estimate density if the density itself is not provided.
    """
    cfg = {
        "TEMP": {"density_inversion": {"threshold": -0.03}},
        "PSAL": {"density_inversion": {"threshold": -0.03}},
    }
    profile = DummyData()
    pqc = ProfileQC(profile, cfg=cfg)

    for v in ("TEMP", "PSAL"):
        assert "density_inversion" in pqc.flags[v]
        if not GSW_AVAILABLE:
            assert (pqc.flags[v]["density_inversion"] == 0).all()


# def test_input_types():
#     cfg = {"threshold": 4}
#     compare_input_types(Spike, cfg)
