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


def fuzzyfy(data, features, output, require="all"):
    """
    Notes
    -----
    In the generalize this once the membership combining rules are defined
    in the cfg, so I can decide to use mean or max.
    """
    features_list = list(features.keys())

    N = max([len(data[f]) for f in features_list])

    # The fuzzy set are usually: low, medium, high
    # The membership of each fuzzy set are each feature scaled.
    membership = {f: {} for f in output.keys()}

    for t in features_list:
        for m in membership:
            assert m in features[t], "Missing %s in %s" % (m, features[t])
            if m == "low":
                membership[m][t] = zmf(np.asanyarray(data[t]), features[t][m])
            elif m == "high":
                membership[m][t] = smf(np.asanyarray(data[t]), features[t][m])
            else:
                membership[m][t] = trapmf(np.asanyarray(data[t]), features[t][m])

    # Rule Set
    rules = {}
    # Low: u_low = mean(S_l(spike), S_l(clim)...)
    # u_low = np.mean([weights['spike']['low'],
    #    weights['woa_relbias']['low']], axis=0)
    # Medium: u_medium = mean(S_l(spike), S_l(clim)...)
    # u_medium = np.mean([weights['spike']['medium'],
    #    weights['woa_relbias']['medium']], axis=0)

    for m in [m for m in membership if m != "high"]:
        tmp = np.vstack([membership[m][f] for f in membership[m]])
        if require == "any":
            rules[m] = np.nanmean(tmp, axis=0)
        else:
            rules[m] = np.mean(tmp, axis=0)

    # High: u_high = max(S_l(spike), S_l(clim)...)
    # u_high = np.max([weights['spike']['high'],
    #    weights['woa_relbias']['high']], axis=0)

    tmp = np.vstack([membership["high"][f] for f in membership["high"]])
    if require == "any":
        rules["high"] = np.nanmax(tmp, axis=0)
    else:
        rules["high"] = np.max(tmp, axis=0)

    return rules


def fuzzy_uncertainty(data, features, output, require="all"):
    """Estimate the Fuzzy uncertainty of the given data

    Parameters
    ----------
    data :
    features :
    output :
    require : all or any, optional
        Require all or any of the features to estimate the uncertainty
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

    rules = fuzzyfy(data=data, features=features, output=output, require=require)

    N_out = 100
    output_range = np.linspace(0, 1, N_out)
    Q = {}
    Q["low"] = trimf(output_range, output["low"])
    if "medium" in output:
        Q["medium"] = trimf(output_range, output["medium"])
    Q["high"] = smf(output_range, output["high"])

    idx = np.isfinite([rules[r] for r in rules])
    # This would be the regular fuzzy approach.
    uncertainty = np.nan * np.ones(np.shape(idx)[1:])
    valid = np.nonzero(idx.all(axis=0))[0]
    for i in valid:
        aggregated = np.zeros(N_out)
        for m in rules:
            aggregated = np.fmax(aggregated, np.fmin(rules[m][i], Q[m]))
        if aggregated.sum() > 0:
            uncertainty[i] = defuzz(output_range, aggregated, "bisector")

    return uncertainty
