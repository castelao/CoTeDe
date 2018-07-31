# -*- coding: utf-8 -*-

"""

    Based on Timms 2011, p9597

"The first case in Equation (1) ensures that the cumulative rate of change function is able to quickly respond to degradations in sensor quality, while the second case ensures that it takes a longer time for confidence to return in the measurements from that sensor once the rate of change of the parameter decreases." (Timms 2011)

        Small   S->M            Medium          M->L            Large
Temp    <0.03   0.03 to 0.05    0.05 to 0.07    0.07 to 0.11    >0.11
Cond    <50     50 to 100       100 to 150      150 to 250      >250


Timms 2011 uses k=0.8

if (RoC_small (t) + 0.5 × RoC_medium (t)) < (cRoC_small (t - 1) + 0.5 × cRoC_medium (t - 1)):
    cRoC_i (t) = RoC_i (t)
else
    cRoC_i (t) = (1 - k) × RoC_i(t) + k * cRoC_i(t - 1)

i = small, medium, large
"""

import numpy as np
from numpy import ma


def cum_rate_of_change(x, memory):

    y = ma.fix_invalid(np.ones_like(x) * np.nan)
    y[1:] = ma.absolute(ma.diff(x))

    for i in range(2, y.size):
        if y[i] < y[i-1]:
            y[i] = (1 - memory) * y[i] + memory * y[i-1]

    return y


class CumRateOfChange(object):
    def __init__(self, data, varname, cfg, noflag=False):
        self.data = data
        self.varname = varname
        self.cfg = cfg

        self.set_features()
        if not noflag:
            self.test()

    def keys(self):
        return self.features.keys() + \
            ["flag_%s" % f for f in self.flags.keys()]

    def set_features(self):
        self.features = {
                'cum_rate_of_change': cum_rate_of_change(
                    self.data[self.varname], self.cfg['memory'])}

    def test(self):
        self.flags = {}
        try:
            threshold = self.cfg['threshold']
        except:
            print("Deprecated cfg format. It should contain a threshold item.")
            threshold = self.cfg

        try:
            flag_good = self.cfg['flag_good']
        except:
            flag_good = 1
        try:
            flag_bad = self.cfg['flag_bad']
        except:
            flag_bad = 4

        assert (np.size(threshold) == 1) \
            and (threshold is not None) \
            and (np.isfinite(threshold))

        flag = np.zeros(self.data[self.varname].shape, dtype='i1')
        idx = ma.absolute(self.features['cum_rate_of_change']) > threshold
        flag[np.nonzero(idx)] = flag_bad
        idx = ma.absolute(self.features['cum_rate_of_change']) <= threshold
        flag[np.nonzero(idx)] = flag_good
        flag[ma.getmaskarray(self.data[self.varname])] = 9
        self.flags['cum_rate_of_change'] = flag
