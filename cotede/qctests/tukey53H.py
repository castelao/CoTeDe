# -*- coding: utf-8 -*-

"""
"""

import numpy as np
from numpy import ma

FLAG_GOOD = 1
FLAG_BAD = 4

def tukey53H(x):
    """Spike test Tukey 53H from Goring & Nikora 2002
    """
    N = len(x)

    u1 = ma.masked_all(N)
    for n in range(N-4):
        if x[n:n+5].any():
            u1[n+2] = ma.median(x[n:n+5])

    u2 = ma.masked_all(N)
    for n in range(N-2):
        if u1[n:n+3].any():
            u2[n+1] = ma.median(u1[n:n+3])

    u3 = ma.masked_all(N)
    u3[1:-1] = 0.25*(u2[:-2] + 2*u2[1:-1] + u2[2:])

    Delta = ma.absolute(x-u3)

    return Delta


def tukey53H_norm(x, l=12):
    """Spike test Tukey53H() normalized by the std of the low pass

       l is the number of observations. The default l=12 is trully not
         a big number, but this test foccus on spikes, therefore, any
         variability longer than 12 is something else.
    """
    Delta = tukey53H(x)

    w = np.hamming(l)
    sigma = (np.convolve(x, w, mode='same') / w.sum()).std()

    return Delta/sigma


class Tukey53H(object):
    def __init__(self, data, varname, cfg):
        self.data = data
        self.varname = varname
        self.cfg = cfg

        self.set_features()

    def keys(self):
        return self.features.keys() + \
            ["flag_%s" % f for f in self.flags.keys()]

    def set_features(self):
        self.features = {
                'tukey53H': tukey53H(self.data[self.varname]),
                'tukey53H_norm': tukey53H_norm(self.data[self.varname],
                    l=self.cfg['l']),
                }

    def test(self):
        """

                I slightly modified the Goring & Nikora 2002. It is
                  expected that CTD profiles has a typical depth
                  structure, with a range between surface and bottom.
        """
        self.flags = {}
        try:
            threshold = self.cfg['threshold']
        except:
            print("Deprecated cfg format. It should contain a threshold item.")
            threshold = self.cfg['k']

        assert (np.size(threshold) == 1) and \
                (threshold is not None) and \
                (np.isfinite(threshold))

        try:
            flag_good = self.cfg['flag_good']
        except:
            flag_good = FLAG_GOOD
        try:
            flag_bad = self.cfg['flag_bad']
        except:
            flag_bad = FLAG_BAD

        flag = np.zeros(self.data[self.varname].shape, dtype='i1')
        flag[np.nonzero(self.features['tukey53H_norm'] > threshold)] = \
                flag_bad
        flag[np.nonzero(self.features['tukey53H_norm'] <= threshold)] = \
                flag_good
        flag[ma.getmaskarray(self.data[self.varname])] = 9
        self.flags['tukey53H_norm'] = flag
