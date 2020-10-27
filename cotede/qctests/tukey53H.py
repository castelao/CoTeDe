# -*- coding: utf-8 -*-

"""


Shall I use a decorator??

DATA = [25.32, 25.34, 25.34, 25.31, 24.99, 23.46, 21.85, 17.95, 15.39, 11.08, 6.93, 7.93, 5.71, 3.58, np.nan, 1, 1]


tukey53H(np.array, np.maskedArray, pd.Series, xr.DataArray)


    delta = tukey53H(x)

    w = np.hamming(l)
    sigma = (ma.convolve(x, w, mode="same") / w.sum()).std()

    return delta / sigma
"""

import logging

import numpy as np
from numpy import ma

from cotede.qctests import QCCheckVar

try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except:
    PANDAS_AVAILABLE = False


module_logger = logging.getLogger(__name__)


def tukey53H(x, normalize=False):
    """Spike test Tukey 53H from Goring & Nikora 2002

    Return
    ------
    delta :
        An array with the same shape of input x of the difference between x
        and a smoothed x.
    """
    if isinstance(x, ma.MaskedArray):
        x[x.mask] = np.nan
        x = x.data

    if not PANDAS_AVAILABLE:
        return _tukey53H_numpy(x, normalize=normalize)

    if hasattr(x, "to_series"):
        x = x.to_series()
    elif not isinstance(x, pd.Series):
        x = pd.Series(x)

    u1 = x.reset_index(drop=True).rolling(5, center=True).median()
    u2 = u1.rolling(3, center=True).median()
    u3 = 0.25 * (u2.shift(-1) + 2 * u2 + u2.shift(1))

    delta = x - u3

    if not normalize:
        return np.array(delta)

    sigma = u1.dropna().std(ddof=1)
    return np.array(delta / sigma)


def _tukey53H_numpy(x, normalize=False):
    """Equivalent to tukey53H but without using pandas

    Note
    ----
    - For larger datasets (>1k) like timeseries the pandas alternative can be
      significantly faster.
    """
    if isinstance(x, ma.MaskedArray):
        x[x.mask] = np.nan
        x = x.data

    N = len(x)

    u1 = np.nan * np.ones(N)
    for n in range(N - 4):
        u1[n + 2] = np.median(x[n : n + 5])

    u2 = np.nan * np.ones(N)
    for n in range(N - 2):
        u2[n + 1] = np.median(u1[n : n + 3])

    u3 = np.nan * np.ones(N)
    u3[1:-1] = 0.25 * (u2[:-2] + 2 * u2[1:-1] + u2[2:])

    delta = np.nan * np.ones(N)
    delta[1:-1] = x[1:-1] - u3[1:-1]

    if not normalize:
        return delta

    idx = ~np.isnan(u1)
    if idx.all():
        return np.nan * delta
    sigma = np.std(u1[idx], ddof=1)
    return delta / sigma


def tukey53H_norm(x, l=12):
    """Spike test Tukey53H() normalized by the std of the low pass

    ATTENTION: l option is temporarily deactivated.

       l is the number of observations. The default l=12 is trully not
         a big number, but this test foccus on spikes, therefore, any
         variability longer than 12 is something else.
    """
    return tukey53H(x, normalize=True)


class Tukey53H(QCCheckVar):
    def set_features(self):
        self.features = {
            "tukey53H": tukey53H(self.data[self.varname]),
            "tukey53H_norm": tukey53H_norm(self.data[self.varname], l=self.cfg["l"]),
        }

    def test(self):
        """

                I slightly modified the Goring & Nikora 2002. It is
                  expected that CTD profiles has a typical depth
                  structure, with a range between surface and bottom.
        """
        self.flags = {}
        try:
            threshold = self.cfg["threshold"]
        except KeyError:
            print("Deprecated cfg format. It should contain a threshold item.")
            threshold = self.cfg["k"]

        assert (
            (np.size(threshold) == 1)
            and (threshold is not None)
            and (np.isfinite(threshold))
        )

        flag = np.zeros(self.data[self.varname].shape, dtype="i1")
        feature = np.absolute(self.features["tukey53H"])
        flag[feature > threshold] = self.flag_bad
        flag[feature <= threshold] = self.flag_good
        x = self.data[self.varname]
        flag[ma.getmaskarray(x) | ~np.isfinite(x)] = 9
        self.flags["tukey53H"] = flag
