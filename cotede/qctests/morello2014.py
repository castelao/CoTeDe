# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""A hybrid fuzzy logic method

This method applies a fuzzy logic classification with a modified deffuzification in the end, and it was proposed in the following sequence of papers:

- Timms, G.P., de Souza, P.a., Reznik, L., Smith, D.V., 2011. Auto- mated data quality assessment of marine sensors. Sensors 11, 9589–9602. doi:10.3390/s111009589.
- Morello, E., Lynch, T., Slawinski, D., Howell, B., Hughes, D., Timms, G., 2011. Quantitative quality control (qc) procedures for the australian national reference stations: Sensor data, in: OCEANS 2011, IEEE, Waikoloa, HI. pp. 1–7.
- Morello, E.B., Galibert, G., Smith, D., Ridgway, K.R., Howell, B., Slawin- ski, D., Timms, G.P., Evans, K., Lynch, T.P., 2014. Quality Control (QC) procedures for Australias National Reference Stations sensor dataComparing semi-autonomous systems to an expert oceanographer. Methods Oceanogr. 9, 17–33. doi:10.1016/j.mio.2014.09.001.
"""

import logging

import numpy as np
from numpy import ma

from ..fuzzy import fuzzyfy
from .core import QCCheckVar
from .gradient import gradient
from .spike import spike
from .woa_normbias import woa_normbias

module_logger = logging.getLogger(__name__)


def morello2014(features, cfg=None):
    """
    """
    if (cfg is None) or ("output" not in cfg) or ("features" not in cfg):
        module_logger.debug("Using original Morello2014 coefficients")
        cfg = {
            "output": {"low": None, "high": None},
            "features": {
                "spike": {"weight": 1, "low": [0.07, 0.2], "high": [2, 6]},
                "woa_normbias": {"weight": 1, "low": [3, 4], "high": [5, 6]},
                "gradient": {"weight": 1, "low": [0.5, 1.5], "high": [3, 4]},
            },
        }

    if not np.all([f in features for f in cfg["features"]]):
        module_logger.warning(
            "Not all features (%s) required by morello2014 are available".format(
                cfg["features"].keys()
            )
        )
        raise KeyError

    f = fuzzyfy(features, cfg)

    for level in f:
        if isinstance(f[level], ma.MaskedArray):
            mask = f[level].mask
            f[level] = f[level].data
            f[level][mask] = np.nan

    return f


class Morello2014(QCCheckVar):
    def set_features(self):
        self.features = {}
        self.features["spike"] = spike(self.data[self.varname])
        self.features["gradient"] = gradient(self.data[self.varname])
        woa_comparison = woa_normbias(self.data, self.varname, self.attrs)
        self.features["woa_normbias"] = woa_comparison["woa_normbias"]

    def test(self):
        self.flags = {}

        cfg = self.cfg
        flag = np.zeros(np.shape(self.data[self.varname]), dtype="i1")

        try:
            f = morello2014(self.features, self.cfg)
        except:
            self.flags["morello2014"] = flag
            return

        # This is how Timms and Morello defined the Fuzzy Logic approach
        flag[(f["low"] > 0.5) & (f["high"] < 0.3)] = 2
        flag[(f["low"] > 0.9)] = 1
        # Everything else is flagged 3
        flag[(f["low"] <= 0.5) | (f["high"] >= 0.3)] = 3
        # Missing check if threshold was crossed, to flag as 4
        # The thresholds coincide with the end of the ramp for the fuzzy set
        #   high, hence we can simply
        flag[(f["high"] == 1.0)] = 4

        self.flags["morello2014"] = flag
