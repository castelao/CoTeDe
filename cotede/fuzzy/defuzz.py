# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE_scikit-fuzzy.txt

"""

    This was strongly inspired on scikit-fuzzy by Joshua Warner et.al.,
      and they deserve most of the credits for this.
    The decision to split came from the fact that here we use only few
      functions from scikit-fuzzy, and scikit-fuzzy 0.1.9 stopped to
      work with pypi, breaking all tests and the development process of
      CoTeDe.

"""

import numpy as np

def defuzz(x, mfx, mode):
    """
    Defuzzification of a membership function, returning a defuzzified value
    of the function at x, using various defuzzification methods.

    Parameters
    ----------
    x : 1d array or iterable, length N
        Independent variable.
    mfx : 1d array of iterable, length N
        Fuzzy membership function.
    mode : string
        Controls which defuzzification method will be used.
        * 'centroid': Centroid of area
        * 'bisector': bisector of area
        * 'mom'     : mean of maximum
        * 'som'     : min of maximum
        * 'lom'     : max of maximum

    Returns
    -------
    u : float or int
        Defuzzified result.

    """
    mode = mode.lower()
    x = x.ravel()
    mfx = mfx.ravel()
    n = len(x)
    assert n == len(mfx), 'Length of x and fuzzy membership function must be \
                          identical.'

    if 'centroid' in mode or 'bisector' in mode:
        tot_area = mfx.sum()
        assert tot_area != 0, 'Total area is zero in defuzzification!'

        if 'centroid' in mode:
            return centroid(x, mfx)

        elif 'bisector' in mode:
            tmp = 0
            for k in range(n):
                tmp += mfx[k]
                if tmp >= tot_area / 2.:
                    return x[k]

    elif 'mom' in mode:
        return np.mean(x[mfx == mfx.max()])

    elif 'som' in mode:
        tmp = x[mfx == mfx.max()]
        return tmp[tmp == np.abs(tmp).min()][0]

    elif 'lom' in mode:
        tmp = x[mfx == mfx.max()]
        return tmp[tmp == np.abs(tmp).max()][0]

    else:
        raise ValueError('The input for `mode`, %s, was incorrect.' % (mode))
