# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
"""

import numpy as np
from numpy.testing import assert_allclose

from cotede.fuzzy import fuzzyfy


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


def test_fuzzyfy():
    features = {"f1": np.array([1.0]), "f2": np.array([5.2]), "f3": np.array([0.9])}

    rules = fuzzyfy(features, **CFG)
    assert_allclose(rules["low"], [0.226666666])
    assert_allclose(rules["medium"], [0.733333333])
    assert_allclose(rules["high"], [0.08000000])


def test_fuzzyfy_with_nan():
    features = {
        "f1": np.array([1.0, np.nan, 1.0, 1.0, np.nan]),
        "f2": np.array([5.2, 5.2, np.nan, 5.2, np.nan]),
        "f3": np.array([0.9, 0.9, 0.9, np.nan, np.nan]),
    }

    rules = fuzzyfy(features, **CFG)
    assert_allclose(rules["low"], [0.22666667, np.nan, np.nan, np.nan, np.nan])
    assert_allclose(rules["medium"], [0.733333333, np.nan, np.nan, np.nan, np.nan])
    assert_allclose(rules["high"], [0.08000000, np.nan, np.nan, np.nan, np.nan])

    rules = fuzzyfy(features, **CFG, require="any")
    assert_allclose(rules["low"], [0.22666667, 0.34, 0.34, 0, np.nan])
    assert_allclose(rules["medium"], [0.733333333, 0.6, 0.7, 0.9, np.nan])
    assert_allclose(rules["high"], [0.08, 0.08, 0, 0.08, np.nan])


def test_fuzzyfy_all_nan():
    features = {
        "f1": np.array([np.nan]),
        "f2": np.array([np.nan]),
        "f3": np.array([np.nan]),
    }

    rules = fuzzyfy(features, **CFG)
    assert_allclose(rules["low"], [np.nan])
    assert_allclose(rules["medium"], [np.nan])
    assert_allclose(rules["high"], [np.nan])


"""

    # FIXME: If there is only one feature, it will return 1 value
    #          instead of an array with N values.
"""
