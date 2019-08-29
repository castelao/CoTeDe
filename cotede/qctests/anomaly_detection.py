# -*- coding: utf-8 -*-

"""
    Quality Control based on anomaly detection
"""

import logging

import numpy as np
#from numpy import ma
from cotede.anomaly_detection import estimate_anomaly


module_logger = logging.getLogger(__name__)

def anomaly_detection(features, cfg):
    """

        Must decide where to set the flags.
    """

    prob = estimate_anomaly(features, params = cfg['features'])
    #flag = np.zeros(self.input[v].shape, dtype='i1')
    flag = np.zeros(prob.shape, dtype='i1')

    flag[np.nonzero(prob >= cfg['threshold'])] = 1
    flag[np.nonzero(prob < cfg['threshold'])] = 4

    return prob, flag
