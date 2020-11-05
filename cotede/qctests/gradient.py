#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""

"""

import logging

import numpy as np
from numpy import ma

from cotede.qctests import QCCheckVar

try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

module_logger = logging.getLogger(__name__)


def gradient(x):
    return curvature(x)


def _curvature_pandas(x):
    """Equivalent to curvature() but using pandas

    It looks like the numpy implementation is faster even for larger datasets,
    so the default is with numpy.

    Note
    ----
    - In the future this will be useful to handle specific window widths.
    """
    if isinstance(x, ma.MaskedArray):
        x[x.mask] = np.nan
        x = x.data

    if not PANDAS_AVAILABLE:
        return curvature(x)

    if hasattr(x, "to_series"):
        x = x.to_series()
    elif not isinstance(x, pd.Series):
        x = pd.Series(x)

    y = np.nan * x
    y = x - (x.shift(1) + x.shift(-1)) / 2.0
    return np.array(y)


def curvature(x):
    """Curvature of a timeseries

    This test is commonly known as gradient for historical reasons, but that
    is a bad name choice since it is not the actual gradient, like:
    d/dx + d/dy + d/dz,
    but as defined by GTSPP, EuroGOOS and others, which is actually the
    curvature of the timeseries..

    Note
    ----
    - Pandas.Series operates with indexes, so it should be done different. In
      that case, call for _curvature_pandas.
    """
    if isinstance(x, ma.MaskedArray):
        x[x.mask] = np.nan
        x = x.data

    if PANDAS_AVAILABLE and isinstance(x, pd.Series):
        return _curvature_pandas(x)

    x = np.atleast_1d(x)
    y = np.nan * x
    y[1:-1] = x[1:-1] - (x[:-2] + x[2:]) / 2.0
    return y


class Gradient(QCCheckVar):
    def set_features(self):
        self.features = {"gradient": curvature(self.data[self.varname])}

    def test(self):
        self.flags = {}
        try:
            threshold = self.cfg["threshold"]
        except KeyError:
            module_logger.debug(
                "Deprecated cfg format. It should contain a threshold item."
            )
            threshold = self.cfg

        assert (
            (np.size(threshold) == 1)
            and (threshold is not None)
            and (np.isfinite(threshold))
        )

        flag = np.zeros_like(self.data[self.varname], dtype="i1")
        feature = np.absolute(self.features["gradient"])
        flag[feature > threshold] = self.flag_bad
        flag[feature <= threshold] = self.flag_good
        x = np.atleast_1d(self.data[self.varname])
        flag[ma.getmaskarray(x) | ~np.isfinite(x)] = 9
        self.flags["gradient"] = flag
