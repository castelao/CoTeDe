# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

import numpy as np
from numpy import ma

from .qctests import QCCheckVar


def constant_cluster_size(x, tol=0):
    """Estimate the cluster size with (nearly) constant value

       Returns how many consecutive neighbor values are within a given
         tolerance range. Note that invalid values, like NaN, are ignored.
    """
    assert np.ndim(x) == 1, 'Not ready for more than 1 dimension'

    # Adding a tolerance to handle roundings due to different numeric types.
    tol = tol + 1e-5 * tol

    ivalid = np.nonzero(~ma.getmaskarray(ma.fix_invalid(x)))[0]
    dx = np.diff(x[ivalid])

    cluster_size = np.zeros(np.shape(x), dtype='i')
    for i, iv in enumerate(ivalid):
        idx = np.absolute(dx[i:].cumsum()) > tol
        if True in idx:
            cluster_size[iv] += np.nonzero(idx)[0].min()
        else:
            cluster_size[iv] += idx.size
        idx = np.absolute(dx[0:i][::-1].cumsum()) > tol
        if True in idx:
            cluster_size[iv] += np.nonzero(idx)[0].min()
        else:
            cluster_size[iv] += idx.size
    return cluster_size


class ConstantClusterSize(QCCheckVar):
    def set_features(self):
        cluster_size = constant_cluster_size(self.data[self.varname])
        N = ma.compressed(self.data[self.varname]).size
        cluster_fraction = cluster_size / N

        self.features = {'constant_cluster_size': cluster_size,
                         'constant_cluster_fraction': cluster_fraction,
                         }

    def test(self):
        self.flags = {}
        threshold = self.cfg['threshold']

        # assert (np.size(threshold) == 1) \
        #        and (threshold is not None) \
        #        and (np.isfinite(threshold))

        if isinstance(threshold, str) and (threshold[-1] == '%'):
            threshold = float(threshold[:-1]) * 1e-2
            feature_name = 'constant_cluster_fraction'
        else:
            feature_name = 'constant_cluster_size'

        flag = np.zeros(self.data[self.varname].shape, dtype='i1')
        feature = self.features[feature_name]
        flag[np.nonzero(feature > threshold)] = self.flag_bad
        flag[np.nonzero(feature <= threshold)] = self.flag_good
        flag[ma.getmaskarray(self.data[self.varname])] = 9
        self.flags[feature_name] = flag
