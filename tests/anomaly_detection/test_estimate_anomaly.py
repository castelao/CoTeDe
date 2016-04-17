#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

import numpy as np
from numpy import ma
import pandas as pd

from cotede.anomaly_detection import estimate_anomaly
from cotede.anomaly_detection import fit_tests


dummy_params = {
    "spike": {
            "model": "exponweib",
            "qlimit": 0.000900,
            "param": [0.517448, 0.801291 , 0.000300, 0.012925]
            },
    "tukey53H_norm": {
            "model": "exponweib",
            "qlimit": 0.001090,
            "param": [0.650092, 0.728563, 0.001090, 0.005681]
            }
    }

dummy_features = {
        "spike": ma.masked_values([-999, -0.4, 0.1, 1.2, np.nan, 0.2], -999),
        }


def test_fit_tests():
    f1 = fit_tests(dummy_features, q=.25)
    f2 = fit_tests(pd.DataFrame(dummy_features), q=.25)
    assert f1 == f2
    assert np.allclose(f1['spike']['qlimit'], -0.0249999999999999)
    assert np.allclose(f1['spike']['param'], (24.42374861845073,
        0.049435717819356101, 0.099999997902377152, 3.3543862066137581e-15))


def test_estimate_anomaly():
    f1 = estimate_anomaly(dummy_features,
            {'spike': dummy_params['spike']})
    f2 = estimate_anomaly(pd.DataFrame(dummy_features),
            {'spike': dummy_params['spike']})

    assert ma.allclose(f1, f2)
    assert ma.allclose(f1,
            ma.masked_values([-999, 0.0, -5.797359001920061,
                -57.564627324851145, -999, -9.626760611162082], -999))


def test_estimate_anomaly_pandas():
    features = pd.DataFrame(
            {'spike': [0, 1, -.5],
                'tukey53H_norm': [-1, 0, 2]})
    output = estimate_anomaly(features, dummy_params)

    assert len(output) == len(features[features.keys()[0]])
    assert type(output) == ma.MaskedArray
    assert ~ma.getmaskarray(output).any()


def test_estimate_anomaly_dict():
    features = {'spike': [0, 1, -.5],
                'tukey53H_norm': [-1, 0, 2]
                }
    output = estimate_anomaly(features, dummy_params)

    assert len(output) == len(features[features.keys()[0]])
    assert type(output) == ma.MaskedArray
    assert ~ma.getmaskarray(output).any()


def test_estimate_anomaly_maskedarray():
    features = {'spike': ma.MaskedArray([0, 1, -.5], mask=[False, True, False]),
                'tukey53H_norm': ma.MaskedArray([-1, 0, 2], mask=[False, True, False]),
                }
    output = estimate_anomaly(features, dummy_params)

    assert len(output) == len(features[features.keys()[0]])
    assert type(output) == ma.MaskedArray
    # If all features for one measurement are masked, the estimated probability
    #   will be masked, like in the second position of this example
    assert (output.mask == [False, True, False]).all()

    features['spike'].mask[1] = False
    output = estimate_anomaly(features, dummy_params)

    assert len(output) == len(features[features.keys()[0]])
    assert type(output) == ma.MaskedArray
    # But if is there at least one of features valid, it returns a valid value
    # Compare this example with the previous where spike[1] is not masked
    #   anymore.
    assert ~ma.getmaskarray(output).any()
