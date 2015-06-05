# -*- coding: utf-8 -*-

"""
"""

import numpy as np
from numpy import ma


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


def tukey53H_norm(x, k=1.5, l=12):
    """Spike test Tukey53H() normalized by the std of the low pass

       l is the number of observations. The default l=12 is trully not
         a big number, but this test foccus on spikes, therefore, any
         variability longer than 12 is something else.
    """
    Delta = tukey53H(x)

    w = np.hamming(l)
    sigma = (np.convolve(x, w, mode='same') / w.sum()).std()

    return Delta/(k*sigma)
