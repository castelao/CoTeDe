# -*- coding: utf-8 -*-

"""

    Where is this test from? GTSPP?
"""
import logging

import numpy as np
from numpy import ma

from .qctests import QCCheckVar

module_logger = logging.getLogger(__name__)


def profile_envelop(data, cfg, varname):
    """

        Probably not the best way to do this, but works for now.
    """
    # assert varname in data.keys()

    z = data["PRES"]
    x = data[varname]

    flag = np.zeros(z.shape, dtype="i1")

    for layer in cfg["layers"]:
        ind = np.nonzero(eval("(z %s) & (z %s)" % (layer[0], layer[1])))[0]
        f = eval("(x[ind] > %s) & (x[ind] < %s)" % (layer[2], layer[3]))

        flag[ind[f == True]] = 1
        flag[ind[f == False]] = 4

    flag[ma.getmaskarray(x)] = 9

    return flag


class ProfileEnvelop(QCCheckVar):
    def test(self):
        self.flags = {}

        z = self.data["PRES"]
        x = self.data[self.varname]

        assert z.shape == x.shape

        flag = np.zeros(x.shape, dtype="i1")

        assert "layers" in self.cfg, "Profile envelop cfg requires layers"

        for layer in self.cfg['layers']:
            ind = np.nonzero(eval("(z %s) & (z %s)" % (layer[0], layer[1])))[0]
            f = eval("(x[ind] > %s) & (x[ind] < %s)" % (layer[2], layer[3]))

            flag[ind[f == True]] = self.flag_good
            flag[ind[f == False]] = self.flag_bad

        flag[ma.getmaskarray(self.data[self.varname])] = 9
        self.flags["profile_envelop"] = flag

        return
