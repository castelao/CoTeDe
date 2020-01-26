#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""Deepest Pressure

   Test from Argo QC manual 2.9.1
"""

import logging

import numpy as np
from numpy import ma

from .qctests import QCCheckVar

module_logger = logging.getLogger(__name__)


class DeepestPressure(QCCheckVar):
    """Deepest measurable pressure

       Some probes have a maximum operational depth, which can be used as a
       hard threshold. For instance, on Argo, Solo operates up to 2000m while
       Deep Solo goes up to 6000m.
    """
    flag_bad = 3

    def test(self, tol_frac=0.1):
        """Apply test to define flags

           tol_frac is the tolerance fraction of the threshold. Argo uses a
           tolerance of 10%, so that every measurement deeper than the 110%
           of the threshold fails this flag.
        """
        self.flags = {}

        assert "PRES" in self.data.keys(), "Missing pressure record"

        threshold = self.cfg["threshold"]
        assert (
            (np.size(threshold) == 1)
            and (threshold is not None)
            and (np.isfinite(threshold))
        )
        threshold *= (1 + tol_frac)

        flag = np.zeros(self.data[self.varname].shape, dtype="i1")
        feature = self.data["PRES"]
        flag[np.nonzero(feature > threshold)] = self.flag_bad
        flag[np.nonzero(feature <= threshold)] = self.flag_good
        flag[ma.getmaskarray(self.data[self.varname])] = 9
        self.flags["deepest_pressure"] = flag
