# -*- coding: utf-8 -*-

"""
    Quality Control based on anomaly detection
"""


import numpy as np
from cotede.fuzzy import fuzzyfy


def morello2014(features, cfg):
    """

        FIXME: Think about, should I return 0, or have an assert, and at qc.py
          all qc tests are applied with a try, and in case it fails it flag
          0s.

    """
    # for f in cfg['features']:
    #    assert f in features, \
    #            "morello2014 requires feature %s, which is not available" \
    #            % f

    if not np.all([f in features for f in cfg["features"]]):
        print(
            "Not all features (%s) required by morello2014 are available"
            % cfg["features"].keys()
        )
        try:
            return np.zeros(features[features.keys()[0]].shape, dtype="i1")
        except:
            return 0

    f = fuzzyfy(features, cfg)

    # This is how Timms and Morello defined the Fuzzy Logic approach
    # flag = np.zeros(N, dtype='i1')
    # Flag must be np.array, not a ma.array.
    flag = np.zeros(features[list(features.keys())[0]].shape, dtype="i1")

    flag[(f["low"] > 0.5) & (f["high"] < 0.3)] = 2
    flag[(f["low"] > 0.9)] = 1
    # Everything else is flagged 3
    flag[(f["low"] <= 0.5) | (f["high"] >= 0.3)] = 3
    # Missing check if threshold was crossed, to flag as 4
    # The thresholds coincide with the end of the ramp for the fuzzy set high,
    #   hence we can simply
    flag[(f["high"] == 1.0)] = 4

    return flag
