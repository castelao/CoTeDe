# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst


import numpy as np
from numpy import ma


def constant_cluster_size(x, tol=0):
    """ Estimate the cluster size with constant value

        Returns how many consecutive neighbor values are equal or less than
          the given tolerance difference.
    """
    dx = np.diff(x)
    fwd = np.zeros(np.shape(x), dtype='i')
    bwd = np.zeros(np.shape(x), dtype='i')
    idx = np.nonzero(np.absolute(dx) <= tol)[0]

    for i in idx:
        fwd[i+1] = 1 + fwd[i]
    for i in idx[::-1]:
        bwd[i] = 1 + bwd[i+1]

    return fwd + bwd


class ConstantClusterSize(object):
    def __init__(self, data, varname, cfg, autoflag=True):
        self.data = data
        self.varname = varname
        self.cfg = cfg

        self.set_features()

    def keys(self):
        return self.features.keys() + \
            ["flag_%s" % f for f in self.flags.keys()]

    def set_features(self):
        self.features = {
                'constant_cluster_size': constant_cluster_size(
                    self.data[self.varname])}

    def test(self):
        self.flags = {}
        try:
            threshold = self.cfg['threshold']
        except:
            print("Deprecated cfg format. It should contain a threshold item.")
            threshold = self.cfg

        try:
            flag_good = self.cfg['flag_good']
        except:
            flag_good = 1
        try:
            flag_bad = self.cfg['flag_bad']
        except:
            flag_bad = 4

        assert (np.size(threshold) == 1) \
               and (threshold is not None) \
               and (np.isfinite(threshold))

        flag = np.zeros(self.data[self.varname].shape, dtype='i1')
        idx = np.nonzero(self.features['constant_cluster_size'] > threshold)
        flag[idx] = flag_bad
        idx = np.nonzero(self.features['constant_cluster_size'] <= threshold)
        flag[idx] = flag_good
        flag[ma.getmaskarray(self.data[self.varname])] = 9
        self.flags['constant_cluster_size'] = flag
