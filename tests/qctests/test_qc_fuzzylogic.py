# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

""" Check Fuzzy Logic QC test
"""

from datetime import timedelta

from hypothesis import given, settings, strategies as st
from hypothesis.extra.numpy import arrays, array_shapes
import numpy as np

from cotede.qctests import FuzzyLogic, fuzzylogic
from .compare import compare_input_types, compare_compound_feature_input_types
from ..data import DummyData


CFG = {
                "output": {
                    "low": {'type': 'trimf', 'params': [0.0, 0.225, 0.45]},
                    "medium": {'type': 'trimf', 'params': [0.275, 0.5, 0.725]},
                    "high": {'type': 'smf', 'params': [0.55, 0.775]}
                },
                "features": {
                    "spike": {
                        "weight": 1,
                        "low": {'type': 'zmf', 'params': [0.07, 0.2]},
                        "medium": {'type': 'trapmf', 'params': [0.07, 0.2, 2, 6]},
                        "high": {'type': 'smf', 'params': [2, 6]}
                    },
                    "woa_normbias": {
                        "weight": 1,
                        "low": {'type': 'zmf', 'params': [3, 4]},
                        "medium": {'type': 'trapmf', 'params': [3, 4, 5, 6]},
                        "high": {'type': 'smf', 'params': [5, 6]}
                    },
                    "gradient": {
                        "weight": 1,
                        "low": {'type': 'zmf', 'params': [0.5, 1.5]},
                        "medium": {'type': 'trapmf', 'params': [0.5, 1.5, 3, 4]},
                        "high": {'type': 'smf', 'params': [3, 4]}
                    }
                }
            }


def test_standard_dataset():
    features = {
        "fuzzylogic": np.array([np.nan, 0.22222222, 0.22222222, 0.22222222, 0.23232323, 0.22222222, 0.26262626, 0.22222222, 0.24242424, 0.22222222, 0.29292929, 0.43434343, 0.22222222, np.nan, np.nan])
    }
    flags = {
        "fuzzylogic": np.array(
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 3, 1, 0, 0], dtype="i1"
        )
    }

    profile = DummyData()

    y = FuzzyLogic(profile, "TEMP", cfg=CFG)

    assert 'fuzzylogic' in y.flags
    assert np.shape(profile["TEMP"]) == np.shape(y.flags["fuzzylogic"])

    for f in features:
        assert np.allclose(y.features[f], features[f], equal_nan=True)
    for f in flags:
        assert np.allclose(y.flags[f], flags[f], equal_nan=True)


def test_feature_input_types():
    x = np.array([0, 1, -1, 2, -2, 3, 2, 4, 0, np.nan])
    features = {"spike": x, "woa_normbias": x, "gradient": x}
    compare_compound_feature_input_types(fuzzylogic, features, cfg=CFG)


@given(data=arrays(dtype=np.float, shape=array_shapes(min_dims=2, max_dims=2, min_side=3), elements=st.floats(allow_infinity=True, allow_nan=True)))
@settings(deadline=timedelta(milliseconds=500))
def test_feature_input_types(data):
    data = {"spike": data[:,0], "woa_normbias": data[:,1], "gradient": data[:,2]}
    compare_compound_feature_input_types(fuzzylogic, data=data, cfg=CFG)


def test_input_types():
    # compare_tuple(FuzzyLogic, cfg=CFG)
    compare_input_types(FuzzyLogic, cfg=CFG)
