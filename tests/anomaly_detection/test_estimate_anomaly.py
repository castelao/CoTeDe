#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

from numpy import ma
import pandas as pd

from cotede.anomaly_detection import estimate_anomaly


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
