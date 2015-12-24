# -*- coding: utf-8 -*-

"""
    Quality Control based on anomaly detection
"""


import numpy as np
#from numpy import ma
from cotede.fuzzy import fuzzyfy


def morello2014(features, cfg):
    """

    """

    f = fuzzyfy(features, cfg)

    ## This is how Timms and Morello defined the Fuzzy Logic approach
    #flag = np.zeros(self.input[v].shape, dtype='i1')
    #flag = np.zeros(N, dtype='i1')
    flag = np.zeros(features[features.keys()[0]].shape, dtype='i1')

    flag[(f['low'] > 0.9)] = 1
    flag[(f['low'] > 0.5) & (f['high'] < 0.3)] = 2
    # Missing check if threshold was crossed, to flag as 4
    # Everything else is flagged 3
    ind = flag == 0
    for f in features:
        ind = ind & ~features[f].mask
    flag[ind] = 3

    return flag
