# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""Provile Envelop QC test

I believe that this test was first described by GTSPP, which define minimum
and maximum ranges for different depth layers. The concept is that near the
surface one should expect more variability, thus a wider range.
"""

import logging

import numpy as np
from numpy import ma

from .qctests import QCCheckVar

module_logger = logging.getLogger(__name__)


class ProfileEnvelop(QCCheckVar):
    def test(self):
        self.flags = {}

        x = self.data[self.varname]
        if isinstance(x, ma.MaskedArray):
            x[x.mask] = np.nan
            x = x.data
        x = np.atleast_1d(x)

        z = self.data["PRES"]
        if isinstance(z, ma.MaskedArray):
            if z.mask.any():
                mask = np.ones_like(z, dtype="float32")
                mask[z.mask] = np.nan
                z = z * mask
            z = z.data
        z = np.atleast_1d(z)

        assert np.shape(z) == np.shape(x)

        assert "layers" in self.cfg, "Profile envelop cfg requires layers"

        flag = np.zeros(np.shape(x), dtype="i1")
        for layer in self.cfg["layers"]:
            ind = np.nonzero(eval("(z %s) & (z %s)" % (layer[0], layer[1])))[0]
            f = eval("(x[ind] > %s) & (x[ind] < %s)" % (layer[2], layer[3]))

            flag[ind[f == True]] = self.flag_good
            flag[ind[f == False]] = self.flag_bad

        flag[ma.getmaskarray(x) | ~np.isfinite(x)] = 9
        self.flags["profile_envelop"] = flag
