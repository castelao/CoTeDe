# -*- coding: utf-8 -*-

""" The tests itself to QC the data
"""

import numpy as np
from numpy import ma

def step(x):
    y = ma.masked_all(x.shape, dtype=x.dtype)
    y[1:] = ma.diff(x)
    return y


def gradient(x):
    y = ma.masked_all(x.shape, dtype=x.dtype)
    y[1:-1] = np.abs(x[1:-1] - (x[:-2] + x[2:])/2.0)
    # ATENTION, temporary solution
    #y[0]=0; y[-1]=0
    return y


def spike(x):
    y = ma.masked_all(x.shape, dtype=x.dtype)
    y[1:-1] = np.abs(x[1:-1] - (x[:-2] + x[2:])/2.0) - \
                np.abs((x[2:] - x[:-2])/2.0)
    # ATENTION, temporary solution
    #y[0]=0; y[-1]=0
    return y


def bin_spike(x, l):
    """

        Dummy way to avoid warnings when x[ini:fin] are all masked.
        Improve this in the future.
    """
    N = len(x)
    bin = ma.masked_all(N)
    half_window = l/2
    for i in range(half_window, N-half_window):
        ini = max(0, i - half_window)
        fin = min(N, i + half_window)
        if ~x[ini:fin].mask.any():
            bin[i] = x[i] - ma.median(x[ini:fin])
            #bin_std[i] = (T[ini:fin]).std()

    return bin
