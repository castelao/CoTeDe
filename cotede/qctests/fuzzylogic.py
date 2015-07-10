# -*- coding: utf-8 -*-

"""

    Based on Timms 2011, Morello 2011, Morello 2014
"""

#import numpy as np
#from numpy import ma


def fuzzylogic(data, v, cfg):
    import skfuzzy as fuzz
    import pdb; pdb.set_trace()
    print cfg

    from cotede.qctests import spike
    s = spike(data[v])

    s_low = fuzz.trapmf(s, cfg['spike']['small'])
    s_medium = fuzz.trapmf(s, cfg['spike']['medium'])
    s_high = fuzz.trapmf(s, cfg['spike']['high'])

    # Rule Set

    u_low = s_low   # mean(s_low, RC_low, clim_low)
    u_medium = s_medium   # mean(s_medium, RC_medium, clim_medium)
    u_high = s_high   # max(s_high, RC_high, clim_high)

    # It's not clear at Morello 2014 what is the operator K()
    # Q is the uncertainty, hence Q_low is the low uncertainty
    # Seems like K() is just a linear factor, which would give the level of uncertainty, like 0.1 for low, 0.5 for medium and 0.9 for high would define weights for each level?! I'm not sure. But the result would be a composite curve, so when the Qs are joinned it would give a curve with the possible values on Q (maybe multiple dimensions) and the y would be the composite result [0, 1].
    Q_low = u_low   # K_low(u_low)
    Q_medium = u_medium   # K_medium(u_medium)
    Q_high = u_high   # K_high(u_high)

    # Bisector

    # They refer to Q_i x_l, which I understand as the uncertainty for each value for each level
    # It looks like the uncertainties of all tests of the three levels are groupped and ordered, and the bisector would be the value that would define the half of the area.
    # Is it x the observed value of hypotetical values?

    #CQ = bisector(Qs, ...
