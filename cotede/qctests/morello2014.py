# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""A hybrid fuzzy logic method

This method applies a fuzzy logic classification with a modified deffuzification in the end, and it was proposed in the following sequence of papers:

- Timms, G.P., de Souza, P.a., Reznik, L., Smith, D.V., 2011. Auto- mated data quality assessment of marine sensors. Sensors 11, 9589–9602. doi:10.3390/s111009589.
- Morello, E., Lynch, T., Slawinski, D., Howell, B., Hughes, D., Timms, G., 2011. Quantitative quality control (qc) procedures for the australian national reference stations: Sensor data, in: OCEANS 2011, IEEE, Waikoloa, HI. pp. 1–7.
- Morello, E.B., Galibert, G., Smith, D., Ridgway, K.R., Howell, B., Slawin- ski, D., Timms, G.P., Evans, K., Lynch, T.P., 2014. Quality Control (QC) procedures for Australias National Reference Stations sensor dataComparing semi-autonomous systems to an expert oceanographer. Methods Oceanogr. 9, 17–33. doi:10.1016/j.mio.2014.09.001.
"""


import numpy as np
from numpy import ma
from ..fuzzy import fuzzyfy


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

    for level in f:
        if isinstance(f[level], ma.MaskedArray):
            mask = f[level].mask
            f[level] = f[level].data
            f[level][mask] = np.nan

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
