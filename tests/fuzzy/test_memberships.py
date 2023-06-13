# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""Test memberships of Fuzzy logic

    Tests to be implemented:
        integer input
        masked input
"""

from hypothesis import given, strategies as st
from hypothesis.extra.numpy import arrays, array_shapes
import numpy as np
from numpy.testing import assert_allclose

from cotede.fuzzy.membership_functions import smf, zmf, trimf, trapmf


def test_smf():
    x = [-9, -6.3, -4, 4, 5.1, 0.1]
    p = [-6.3, 4]
    test = smf(x, p)
    expected = [0, 0, 0.09972665, 1., 1, 0.71326232]
    assert_allclose(test, expected)


def test_zmf():
    x = [-9, -6.3, -4, 4, 5.1, 0.1]
    p = [-6.3, 4]
    test = zmf(x, p)
    expected = [1., 1., 0.90027335, 0.0, 0, 0.28673768]
    assert_allclose(test, expected)


def test_trimf():
    x = [-9, -6.3, -4, 4, 5.1, 0.1]
    p = [-6.3, 0, 4]
    test = trimf(x, p)
    expected = [0., 0., 0.36507937, 0.0, 0., 0.975]
    assert_allclose(test, expected)


def test_trapmf():
    x = [-9, -6.3, -4, 4, 5.1, 0.1]
    p = [-6.3, -1, 0, 2]
    test = trapmf(x, p)
    expected = [0., 0., 0.43396226, 0.0, 0., 0.95]
    assert_allclose(test, expected)


@given(
    x=arrays(
        dtype=float,
        shape=array_shapes(),
        elements=st.floats(allow_infinity=True, allow_nan=True),
    ),
    p=arrays(
        dtype=float,
        shape=4,
        elements=st.floats(allow_infinity=False, allow_nan=False),
        unique=True,
    ),
)
def test_membership_nan(x, p):
    """Nan input results in NaN outputs

    Test random combinations of inputs and parameters. Every NaN input must
    reflect in NaN output of the membership, otherwise the output must be
    between 0 and 1.
    """
    for f, psize in ((smf, 2), (zmf, 2), (trimf, 3), (trapmf, 4)):
        y = f(x, sorted(p[:psize]))

        # Output has the same shape
        assert np.shape(x) == np.shape(y)

        # NaN inputs results in NaN outputs
        idx = np.isnan(x)
        assert np.all(np.isnan(y[idx]))

        # Possible values range between [0, 1]
        assert np.all(
            (y[~idx] >= 0) & (y[~idx] <= 1)
        ), "Failed range output for {}".format(f)
