# -*- coding: utf-8 -*-

"""

    Based on Timms 2011, Morello 2011, Morello 2014
"""

import numpy as np
from numpy import ma


def fuzzylogic(features, v, cfg):
    import skfuzzy as fuzz

    features_list = cfg['features'].keys()
    N = features[features_list[0]].size

    membership = {'low': {}, 'medium': {}, 'high': {}}
    for t in features_list:
        membership['low'][t] = fuzz.trapmf(features[t], cfg['features'][t]['small'])
        membership['medium'][t] = fuzz.trapmf(features[t], cfg['features'][t]['medium'])
        membership['high'][t] = fuzz.trapmf(features[t], cfg['features'][t]['high'])

    # Rule Set
    rules = {}
    # Low: u_low = mean(S_l(spike), S_l(clim)...)
    #u_low = np.mean([weights['spike']['low'],
    #    weights['woa_relbias']['low']], axis=0)

    tmp = membership['low'][features_list[0]]
    for f in features_list[1:]:
        tmp = np.vstack((tmp, membership['low'][f]))

    rules['low'] = np.mean(tmp, axis=0)

    # Medium: u_medium = mean(S_l(spike), S_l(clim)...)
    #u_medium = np.mean([weights['spike']['medium'],
    #    weights['woa_relbias']['medium']], axis=0)

    tmp = membership['medium'][features_list[0]]
    for f in features_list[1:]:
        tmp = np.vstack((tmp, membership['medium'][f]))

    rules['medium'] = np.mean(tmp, axis=0)

    # High: u_high = max(S_l(spike), S_l(clim)...)
    #u_high = np.max([weights['spike']['high'],
    #    weights['woa_relbias']['high']], axis=0)

    tmp = membership['high'][features_list[0]]
    for f in features_list[1:]:
        tmp = np.vstack((tmp, membership['high'][f]))

    rules['high'] = np.max(tmp, axis=0)


    # It's not clear at Morello 2014 what is the operator K()
    # Q is the uncertainty, hence Q_low is the low uncertainty
    # Seems like K() is just a linear factor, which would give the level of uncertainty, like 0.1 for low, 0.5 for medium and 0.9 for high would define weights for each level?! I'm not sure. But the result would be a composite curve, so when the Qs are joinned it would give a curve with the possible values on Q (maybe multiple dimensions) and the y would be the composite result [0, 1].
    #Q_low = 0.1 * u_low   # K_low(u_low)
    #Q_medium = 0.5 * u_medium   # K_medium(u_medium)
    #Q_high = 0.9 *u_high   # K_high(u_high)

    # Bisector

    # They refer to Q_i x_l, which I understand as the uncertainty for each value for each level
    # It looks like the uncertainties of all tests of the three levels are groupped and ordered, and the bisector would be the value that would define the half of the area.
    # Is it x the observed value of hypotetical values?

    #CQ = bisector(Qs, ...

    output_range = np.arange(0, 1, 0.01)
    output = {}
    output['low'] = fuzz.trimf(output_range, cfg['output']['small'])
    output['medium'] = fuzz.trimf(output_range, cfg['output']['medium'])
    output['high'] = fuzz.trimf(output_range, cfg['output']['high'])


    uncertainty = np.empty(N)
    for i in range(N):
        aggregated = np.fmax(np.fmin(rules['high'][i], output['high']),
            np.fmax(np.fmin(rules['medium'][i], output['medium']),
                np.fmin(rules['low'][i], output['low'])))
        uncertainty[i] = fuzz.defuzz(output_range, aggregated, 'bisector')

    flags = np.zeros(N, dtype='i1')
    flags[uncertainty <= 0.5] = 1
    flags[uncertainty > 0.5] = 4

    return flags
