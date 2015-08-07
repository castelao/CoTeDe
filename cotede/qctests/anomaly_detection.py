# -*- coding: utf-8 -*-

"""
    Quality Control based on anomaly detection
"""


import numpy as np
#from numpy import ma
from cotede.anomaly_detection import estimate_anomaly


def anomaly_detection(features, cfg):
    """

        Must decide where to set the flags.
    """

    prob = estimate_anomaly(features, params = cfg['features'])
    #flag = np.zeros(self.input[v].shape, dtype='i1')
    flag = np.zeros(features[features.keys()[0]].shape, dtype='i1')

    flag[np.nonzero(prob >= cfg['threshold'])] = 1
    flag[np.nonzero(prob < cfg['threshold'])] = 4

    return flag
