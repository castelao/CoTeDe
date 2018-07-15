# -*- coding: utf-8 -*-

"""

    This was initially inspired in the sequel: Timms 2011, Morello 2011,
      Morello 2014. I reproduced their work and also implemented an
      alternative approach using a more traditional defuzzification
      procedure.

"""

import numpy as np
from numpy import ma

from .membership_functions import smf, zmf, trapmf, trimf
from .defuzz import defuzz

def fuzzyfy(features, cfg):
    """

        FIXME: Looks like skfuzzy.trapmf does not handle well masked values.
               I must think better what to do with masked input values. What
               to do when there is one feature, but the other features are
               masked?
    """

    features_list = list(cfg['features'].keys())

    N = features[features_list[0]].size

    # The fuzzy set are usually: low, medium, high
    # The membership of each fuzzy set are each feature scaled.
    membership = {}
    for f in cfg['output'].keys():
        membership[f] = {}

    for t in features_list:
        for m in membership:
            assert m in cfg['features'][t], \
                    "Missing %s in %s" % (m, cfg['features'][t])

            membership[m][t] = ma.masked_all_like(features[t])
            ind = ~ma.getmaskarray(features[t])
            if m == 'low':
                membership[m][t][ind] = zmf(
                        np.asanyarray(features[t])[ind], cfg['features'][t][m])
            elif m == 'high':
                membership[m][t][ind] = smf(
                        np.asanyarray(features[t])[ind],
                        cfg['features'][t][m])
            else:
                membership[m][t][ind] = trapmf(
                        np.asanyarray(features[t])[ind],
                        cfg['features'][t][m])

    # Rule Set
    rules = {}
    # Low: u_low = mean(S_l(spike), S_l(clim)...)
    #u_low = np.mean([weights['spike']['low'],
    #    weights['woa_relbias']['low']], axis=0)

    tmp = membership['low'][features_list[0]]
    for f in features_list[1:]:
        tmp = ma.vstack((tmp, membership['low'][f]))

    # FIXME: If there is only one feature, it will return 1 value
    #          instead of an array with N values.
    rules['low'] = ma.mean(tmp, axis=0)

    # IMPROVE IT: Morello2014 doesn't even use the medium uncertainty,
    #   so no reason to estimate it. In the generalize this once the
    #   membership combining rules are defined in the cfg, so I can
    #   decide to use mean or max.
    if 'medium' in membership:
        # Medium: u_medium = mean(S_l(spike), S_l(clim)...)
        #u_medium = np.mean([weights['spike']['medium'],
        #    weights['woa_relbias']['medium']], axis=0)

        tmp = membership['medium'][features_list[0]]
        for f in features_list[1:]:
            tmp = ma.vstack((tmp, membership['medium'][f]))

        rules['medium'] = ma.mean(tmp, axis=0)

    # High: u_high = max(S_l(spike), S_l(clim)...)
    #u_high = np.max([weights['spike']['high'],
    #    weights['woa_relbias']['high']], axis=0)

    tmp = membership['high'][features_list[0]]
    for f in features_list[1:]:
        tmp = ma.vstack((tmp, membership['high'][f]))

    rules['high'] = ma.max(tmp, axis=0)

    return rules


def fuzzy_uncertainty(features, cfg):
    """

        Temporary solution. Under-development.
    """
    # It's not clear at Morello 2014 what is the operator K()
    # Q is the uncertainty, hence Q_low is the low uncertainty
    # Seems like K() is just a linear factor, which would give the level of uncertainty, like 0.1 for low, 0.5 for medium and 0.9 for high would define weights for each level?! I'm not sure. But the result would be a composite curve, so when the Qs are joinned it would give a curve with the possible values on Q (maybe multiple dimensions) and the y would be the composite result [0, 1].
    # Q_low = 0.1 * u_low   # K_low(u_low)
    # Q_medium = 0.5 * u_medium   # K_medium(u_medium)
    # Q_high = 0.9 *u_high   # K_high(u_high)

    # Bisector

    # They refer to Q_i x_l, which I understand as the uncertainty for each value for each level
    # It looks like the uncertainties of all tests of the three levels are groupped and ordered, and the bisector would be the value that would define the half of the area.
    # Is it x the observed value of hypotetical values?

    # CQ = bisector(Qs, ...

    rules = fuzzyfy(features, cfg)

    N_out = 100
    output_range = np.linspace(0, 1, N_out)
    output = {}
    output['low'] = trimf(output_range, cfg['output']['low'])
    if 'medium' in cfg['output']:
        output['medium'] = trimf(output_range, cfg['output']['medium'])
    output['high'] = smf(output_range, cfg['output']['high'])

    # FIXME: As it is now, it will have no zero flag value. Think about cases
    #   where some values in a profile would not be estimated, hence flag=0
    #   I think skfuzzy does not accept masked arrays?!?! That would be the
    #   limiting factor.

    N = rules[list(rules.keys())[0]].size
    # This would be the classic fuzzy approach.
    uncertainty = ma.masked_all(N)
    for i in range(N):
        aggregated = np.zeros(N_out)
        for m in rules:
            if rules[m][i] is not ma.masked:
                aggregated = np.fmax(aggregated,
                                     np.fmin(rules[m][i], output[m]))
        if aggregated.sum() > 0:
            uncertainty[i] = defuzz(output_range, aggregated, 'bisector')

    return uncertainty
