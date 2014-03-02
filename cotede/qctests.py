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
    N = len(x)
    bin = ma.masked_all(N)
    half_window = l/2
    for i in range(half_window, N-half_window):
        ini = max(0, i - half_window)
        fin = min(N, i + half_window)
        bin[i] = x[i] - ma.median(x[ini:fin])
        #bin_std[i] = (T[ini:fin]).std()

    return bin

def densitystep(S, T, P):
    """
    """
    assert S.shape == T.shape
    assert S.shape == P.shape
    assert S.ndim == 1, "Sorry, I'm not ready yet to handle and array with ndim > 1"

    from fluid.ocean.seawater import _dens0 as dens0
    ds = ma.masked_all(S.shape, dtype=S.dtype)
    rho0 = dens0(s=S, t=T)
    ds[1:] = np.sign(np.diff(P))*np.diff(rho0)
    return ds


def descentPrate(t, p):
    assert t.shape == p.shape, "t and p have different sizes"
    y = ma.masked_all(t.shape, dtype=t.dtype)
    dt = ma.diff(t)
    dp = ma.diff(p)
    y[1:] = dp/dt
    return y


def tukey53H(x):
    """Spike test Tukey 53H from Goring & Nikora 2002
    """
    N = len(x)

    u1 = ma.masked_all(N)
    for n in range(N-4):
        u1[n+2] = ma.median(x[n:n+5])

    u2 = ma.masked_all(N)
    for n in range(N-2):
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
    from maud import window_1Dmean
    sigma = (window_1Dmean(x, l, method='hann')).std()
    return Delta/(k*sigma)
