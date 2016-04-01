# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

import numpy as np
from numpy.testing import assert_allclose
from cotede.fuzzy.membership_functions import smf, zmf, trimf, trapmf


"""
    Tests to be implemented:
        integer input
        masked input
"""

def test_smf():
    x = [-4, 5.1, 0.1]
    p = [-6.3, 4] 
    test = smf(x, p)
    expected = np.array([ 0.09972665, 1., 0.71326232])
    assert_allclose(test, expected)


def test_zmf():
    x = [-4, 5.1, 0.1]
    p = [-6.3, 4] 
    test = zmf(x, p)
    expected = np.array([ 0.90027335, 0., 0.28673768])
    assert_allclose(test, expected)


def test_trimf():
    x = [-4, 5.1, 0.1, 0]
    p = [-6.3, 0, 4] 
    test = trimf(x, p)
    expected = np.array([ 0.36507937, 0., 0.975, 1.])
    assert_allclose(test, expected)


def test_trapmf():
    x = [-4, 5.1, 0.1, 0]
    p = [-6.3, -1, 0, 2] 
    test = trapmf(x, p)
    expected = np.array([ 0.43396226, 0., 0.95, 1.])
    assert_allclose(test, expected)
