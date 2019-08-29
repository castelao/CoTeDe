# -*- coding: utf-8 -*-

"""
    Quality Control based on fuzzy logic.
"""

import numpy as np
from cotede.fuzzy import fuzzy_uncertainty


def fuzzylogic(features, cfg):
    """

        FIXME: Think about, should I return 0, or have an assert, and at qc.py
          all qc tests are applied with a try, and in case it fails it flag
          0s.

    """
    # FIXME: Should I use all or any? Should I still try to apply fuzzy even
    #   when it is missing some of the features? Sounds like the best guess
    #   possible.
    if not np.all([f in features for f in cfg['features']]):
        print("Not all features (%s) required to fuzzyfy are available" %
                cfg['features'].keys())
        try:
            return np.zeros(features[features.keys()[0]].shape, dtype='i1')
        except:
            return 0

    #f = fuzzyfy(features, cfg)
    uncertainty = fuzzy_uncertainty(features, cfg)

    # FIXME: As it is now, it will have no zero flag value. Think about cases
    #   where some values in a profile would not be estimated, hence flag=0
    # I needed to use np.nonzeros because now uncertainty is a masked array,
    #   to accept when a feature is masked.
    flags = np.zeros(
            features[list(cfg['features'].keys())[0]].shape, dtype='i1')
    flags[np.nonzero(uncertainty <= 0.29)] = 1
    flags[np.nonzero((uncertainty > 0.29)  & (uncertainty <= 0.34))] = 2
    flags[np.nonzero((uncertainty > 0.34)  & (uncertainty <= 0.72))] = 3
    flags[np.nonzero(uncertainty > 0.72)] = 4

    return flags
