# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

from datetime import timedelta

from hypothesis import given, settings, strategies as st
from hypothesis.extra.numpy import arrays, array_shapes
import numpy as np
from numpy.testing import assert_allclose

from cotede.fuzzy import fuzzy_uncertainty
from ..qctests.compare import compare_compound_feature_input_types


CFG = {
    "output": {
        "low": [0.0, 0.225, 0.45],
        "medium": [0.275, 0.5, 0.725],
        "high": [0.55, 0.775],
    },
    "features": {
        "f1": {
            "weight": 1,
            "low": [0.07, 0.2],
            "medium": [0.07, 0.2, 2, 6],
            "high": [2, 6],
        },
        "f2": {"weight": 1, "low": [3, 4], "medium": [3, 4, 5, 6], "high": [5, 6]},
        "f3": {
            "weight": 1,
            "low": [0.5, 1.5],
            "medium": [0.5, 1.5, 3, 4],
            "high": [3, 4],
        },
    },
}


def test_fuzzy_uncertainty():
    features = {"f1": np.array([1.0]), "f2": np.array([5.2]), "f3": np.array([0.9])}

    uncertainty = fuzzy_uncertainty(features, **CFG)
    assert_allclose(uncertainty, [0.47474747])


def test_fuzzy_uncertainty_with_nan():
    """How fuzzy_uncertainty responds to NaN depending on require input

    The default is to require all features, thus if anyone is NaN the
    outcome uncertainty will be NaN. If require is defined as any, one
    single valid feature will be enough to define an uncertainty. In both
    cases it returns NaN if all features are NaN.
    """
    features = {
        "f1": np.array([1.0, np.nan, 1.0, 1.0, np.nan]),
        "f2": np.array([5.2, 5.2, np.nan, 5.2, np.nan]),
        "f3": np.array([0.9, 0.9, 0.9, np.nan, np.nan]),
    }

    uncertainty = fuzzy_uncertainty(features, **CFG)
    answer = [0.47474747, np.nan, np.nan, np.nan, np.nan]
    assert_allclose(uncertainty, answer)

    uncertainty = fuzzy_uncertainty(features, **CFG, require="any")
    answer = [0.47474747, 0.44444444, 0.43434343, 0.51515152, np.nan]
    assert_allclose(uncertainty, answer)


@given(
    data=arrays(
        dtype=np.float,
        shape=array_shapes(min_dims=2, max_dims=2, min_side=3),
        elements=st.floats(allow_infinity=True, allow_nan=True),
    )
)
@settings(deadline=timedelta(milliseconds=300))
def test_feature_input_types(data):
    data = {"f1": data[:, 0], "f2": data[:, 1], "f3": data[:, 2]}
    compare_compound_feature_input_types(fuzzy_uncertainty, data=data, **CFG)
