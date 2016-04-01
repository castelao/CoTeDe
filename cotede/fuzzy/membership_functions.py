#!/usr/bin/env python
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
from numpy import ma


def smf(x, p):
    """
    S-function fuzzy membership generator.

    Parameters
    ----------
    x : any sequence
        Independent variable.
    p: list of 2 values
        p[0]: 'foot', where the function begins to climb from zero.
        p[1]: 'ceiling', where the function levels off at 1.

    Returns
    -------
    y : 1d array
        S-function.

    Notes
    -----
    Named such because of its S-like shape.

    """
    assert len(p) == 2, 'smf requires 2 parameters'
    assert p[0] <= p[1], 'p[0] must be <= p[1].'

    x = np.asanyarray(x)
    y = np.ones_like(x)

    idx = x <= p[0]
    y[idx] = 0

    idx = np.logical_and(p[0] <= x, x <= (p[0] + p[1]) / 2.)
    y[idx] = 2. * ((x[idx] - p[0]) / (p[1] - p[0])) ** 2.

    idx = np.logical_and((p[0] + p[1]) / 2. <= x, x <= p[1])
    y[idx] = 1 - 2. * ((x[idx] - p[1]) / (p[1] - p[0])) ** 2.

    return y


def trapmf(x, p):
    """
    Trapezoidal membership function generator.

    Parameters
    ----------
    x : any sequence
        Independent variable.
    p: list of 4 values
        lower than p[0] and higher than p[3] it returns 0
        between p[1] and p[2] it returns 1
        linear transition from p[0] to p[1] and from p[2] to p[3]

    Returns
    -------
    y : 1d array
        Trapezoidal membership function.

    """
    assert len(p) == 4, 'trapmf requires 4 parameters.'
    assert p[0] <= p[1] and p[1] <= p[2] and p[2] <= p[3], \
            'trapmf requires 4 parameters: p[0] <= p[1] <= p[2] <= p[3].'

    x = np.asanyarray(x)
    y = np.ones_like(x)

    idx = np.nonzero(x <= p[1])
    y[idx] = trimf(x[idx], [p[0], p[1], p[1]])

    idx = np.nonzero(x >= p[2])[0]
    y[idx] = trimf(x[idx], [p[2], p[2], p[3]])

    idx = np.nonzero(x < p[0])[0]
    y[idx] = np.zeros(len(idx))

    idx = np.nonzero(x > p[3])[0]
    y[idx] = np.zeros(len(idx))

    return y


def trimf(x, p):
    """
    Triangular membership function generator.

    Parameters
    ----------
    x : any sequence
        Independent variable.
    p: list of 4 values
        lower than p[0] and higher than p[3] it returns 0
        between p[1] and p[2] it returns 1

    Returns
    -------
    y : 1d array
        Triangular membership function.

    """
    assert len(p) == 3, 'trimf requires 3 parameters.'
    assert p[0] <= p[1] and p[1] <= p[2], \
            'trimf requires 3 parameters: p[0] <= p[1] <= p[2].'

    x = np.asanyarray(x)
    y = np.zeros(x.shape)

    # Left side
    if p[0] != p[1]:
        idx = np.nonzero(np.logical_and(p[0] < x, x < p[1]))
        y[idx] = (x[idx] - p[0]) / float(p[1] - p[0])

    # Right side
    if p[1] != p[2]:
        idx = np.nonzero(np.logical_and(p[1] < x, x < p[2]))[0]
        y[idx] = (p[2] - x[idx]) / float(p[2] - p[1])

    idx = np.nonzero(x == p[1])
    y[idx] = 1

    return y


def zmf(x, p):
    """
    Z-function fuzzy membership generator.

    Parameters
    ----------
    x : any sequence
        Independent variable.
    p: list of 2 values
        p[0]: 'foot', where the function begins to climb from zero.
        p[1]: 'ceiling', where the function levels off at 1.

    Returns
    -------
    y : 1d array
        Z-function.

    Notes
    -----
    Named such because of its Z-like shape.

    """
    assert len(p) == 2, 'zmf requires 2 parameters'
    assert p[0] <= p[1], 'p[0] must be <= p[1].'

    x = np.asanyarray(x)
    y = np.ones_like(x)

    idx = np.logical_and(p[0] <= x, x < (p[0] + p[1]) / 2.)
    y[idx] = 1 - 2. * ((x[idx] - p[0]) / (p[1] - p[0])) ** 2.

    idx = np.logical_and((p[0] + p[1]) / 2. <= x, x <= p[1])
    y[idx] = 2. * ((x[idx] - p[1]) / (p[1] - p[0])) ** 2.

    idx = x >= p[1]
    y[idx] = 0

    return y
