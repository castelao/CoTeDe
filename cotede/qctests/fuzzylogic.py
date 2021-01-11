# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
    Quality Control based on fuzzy logic.
"""

import logging

import numpy as np

from .core import QCCheckVar
from .gradient import gradient
from .spike import spike
from .woa_normbias import woa_normbias
from cotede.fuzzy import fuzzy_uncertainty

module_logger = logging.getLogger(__name__)


def fuzzylogic(features, cfg, require="all"):
    """

        FIXME: Think about, should I return 0, or have an assert, and at qc.py
          all qc tests are applied with a try, and in case it fails it flag
          0s.

    """
    require = cfg.get("require", require)

    if (require == "all") and not np.all([f in features for f in cfg["features"]]):
        module_logger.warning(
            "Not all features (%s) required by fuzzy logic are available".format(
                cfg["features"].keys()
            )
        )
        raise KeyError

    uncertainty = fuzzy_uncertainty(
        data=features, features=cfg["features"], output=cfg["output"], require=require
    )

    return uncertainty


class FuzzyLogic(QCCheckVar):
    def set_features(self):
        self.features = {}
        for v in [f for f in self.cfg["features"] if f not in self.features]:
            if v == "woa_bias":
                woa_comparison = woa_normbias(self.data, self.varname, self.attrs)
                self.features[v] = woa_comparison["woa_bias"]
            elif v == "woa_normbias":
                woa_comparison = woa_normbias(self.data, self.varname, self.attrs)
                self.features[v] = woa_comparison["woa_normbias"]
            elif v == "spike":
                self.features[v] = spike(self.data[self.varname])
            elif v == "gradient":
                self.features[v] = gradient(self.data[self.varname])

        self.features["fuzzylogic"] = fuzzylogic(self.features, self.cfg)


    def test(self):
        self.flags = {}
        cfg = self.cfg
        flag = np.zeros(np.shape(self.data[self.varname]), dtype="i1")

        uncertainty = self.features["fuzzylogic"]
        # FIXME: As it is now, it will have no zero flag value. Think about cases
        #   where some values in a profile would not be estimated, hence flag=0
        # I needed to use np.nonzeros because now uncertainty is a masked array,
        #   to accept when a feature is masked.
        flag[np.nonzero(uncertainty <= 0.29)] = 1
        flag[np.nonzero((uncertainty > 0.29) & (uncertainty <= 0.34))] = 2
        flag[np.nonzero((uncertainty > 0.34) & (uncertainty <= 0.72))] = 3
        flag[np.nonzero(uncertainty > 0.72)] = 4

        self.flags["fuzzylogic"] = flag
