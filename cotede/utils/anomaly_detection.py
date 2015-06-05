# -*- coding: utf-8 -*-

"""
"""

import numpy as np
from numpy import ma
#from scipy.stats import norm, rayleigh, expon, halfnorm, exponpow, exponweib
from scipy.stats import exponweib
#from scipy.stats import kstest

from cotede.utils import ProfilesQCPandasCollection
from cotede.misc import combined_flag
from cotede.humanqc import HumanQC

def fit_tests(features, qctests, ind=True, q=0.90, verbose=False):
    """

        Input:
          features: a dictionary like with the numerical results from the
              QC tests. For example, the gradient test values, not the
              flags, but the floats itself, like
              {'gradient': ma.array([.23, .12, .08]), 'spike': ...}
          qctests: The name of the tests to fit. They must be in
              features.keys().
              ['gradient', 'spike', 'woa_bias']
          ind: The features values positions to be considered in the fit.
              It's usefull to eliminate out of range data, or to
              restrict to a subset of the data, like in the calibration
              procedure.
          q: The lowest percentile to be considered. For example, .90
              means that only the top 10% data (i.e. percentiles higher
              than .90) are considered in the fitting.
    """
    output = {}
    for test in qctests:
        samp = features[test][ind & np.isfinite(features[test])]
        ind_top = samp > samp.quantile(q)
        param = exponweib.fit(samp[ind_top])
        output[test] = {'param':param,
                'qlimit': samp.quantile(q)}

        if verbose == True:
            import pylab
            x = np.linspace(samp[ind_top].min(), samp[ind_top].max(), 100)
            pdf_fitted = exponweib.pdf(x, *param[:-2], loc=param[-2], scale=param[-1])
            pylab.plot(x,pdf_fitted,'b-')
            pylab.hist(ma.array(samp[ind_top]), 100, normed=1, alpha=.3)
            pylab.title(test)
            pylab.show()

    return output


def estimate_anomaly(aux, params):
    prob = ma.ones(aux.shape[0])
    for t in params.keys():
        param = params[t]['param']
        ind = np.array(np.isfinite(aux[t]))
        prob[ind] = prob[ind] * \
                exponweib.sf(aux[t][ind], *param[:-2], loc=param[-2], scale=param[-1])
    return prob


def estimate_p_optimal(prob, qc, verbose=False):
    err = []
    P = 10.**np.arange(-12, 0, 0.1)
    for p in P:
        false_negative = (prob < p) & (qc == True)
        false_positive = (prob > p) & (qc == False)
        err.append(np.nonzero(false_negative)[0].size + \
                np.nonzero(false_positive)[0].size)
    err = np.array(err)
    if verbose == True:
        pylab.plot(P, err , 'b'); pylab.show()
    return P[err.argmin()], float(err.min())/prob.size#, {'P': P, 'err': err}


def adjust_anomaly_coefficients(flag_ref, qctests, aux, q=0.90, verbose=False):
    """ Adjust coeficients for Anomaly Detection, and estimate error

        Inputs:
            flag_ref: Reference index. What the Anomaly Detection will try
                   to reproduce. Uses the True and Falses from flag_ref
                   to partition the data to be used to fit, to adjust
                   and to estimate the error.
            qctests: The tests used by the Anomaly Detection. One curve will
                   be fit for each test.
            aux: The auxiliary tests results from the ProfileQCCollection. It
                   is expected that the qctests are present in aux.
            q: The top q extreme tests results to be used on Anom. Detect.
                 For example q=0 will use all the data, while q=0.9 (default)
                 will use the percentile of 0.9, i.e. the top 10% values.

            Output: Returns a dictionary with
                err:
                err_ratio:
                false_negative:
                false_positive:
                p_optimal:
                params:

            Use the functions:
                split_data_groups()
                fit_tests()
                estimate_anomaly()
                estimate_p_optimal()

    """
    indices = split_data_groups(flag_ref)
    params = fit_tests(aux, qctests, indices['ind_fit'], q=q,
            verbose=verbose)
    prob = estimate_anomaly(aux, params)
    if verbose == True:
        pylab.hist(prob); pylab.show()

    p_optimal, test_err = estimate_p_optimal(prob[indices['ind_test']],
            flag_ref[indices['ind_test']])

    # I can extract only .data, since split_data_groups already eliminated
    #   all non valid positions.
    false_negative = (prob[indices['ind_err']] < p_optimal) & \
        (flag_ref[indices['ind_err']].data == True)
    false_positive = (prob[indices['ind_err']] > p_optimal) & \
        (flag_ref[indices['ind_err']].data == False)
    err = np.nonzero(false_negative)[0].size + \
            np.nonzero(false_positive)[0].size
    err_ratio = float(err)/prob[indices['ind_err']].size
    false_negative = (prob < p_optimal) & \
        (flag_ref.data == True) & (ma.getmaskarray(flag_ref)==False)
    false_positive = (prob > p_optimal) & \
        (flag_ref.data == False) & (ma.getmaskarray(flag_ref)==False)

    output = {'false_negative': false_negative,
            'false_positive': false_positive,
            'prob': prob,
            'p_optimal': p_optimal,
            'err': err,
            'err_ratio': err_ratio,
            'params': params}

    return output


def split_data_groups(ind):
    """ Splits randomly the indices into fit, test and error groups

        Return 3 indices set:
            - ind_fit with 60% of the good
            - ind_test with 20% of the good and 50% of the bad
            - ind_eval with 20% of the good and 50% of the bad
    """
    assert ind.dtype == 'bool'

    N = ind.size
    ind_base = np.zeros(N) == 1
    ind_valid = ~ma.getmaskarray(ind)

    # ==== Good data ==================
    ind_good = np.nonzero((ind == True) & ind_valid)[0]
    N_good = ind_good.size
    perm = np.random.permutation(N_good)
    N_fit = int(round(N_good*.6))
    N_test = int(round(N_good*.2))
    ind_fit = ind_base.copy()
    ind_fit[ind_good[perm[:N_fit]]] = True
    ind_test = ind_base.copy()
    ind_test[ind_good[perm[N_fit:-N_test]]] = True
    ind_err = ind_base.copy()
    ind_err[ind_good[perm[-N_test:]]] = True

    # ==== Bad data ===================
    ind_bad = np.nonzero((ind == False) & ind_valid)[0]
    N_bad = ind_bad.size
    perm = np.random.permutation(N_bad)
    N_test = int(round(N_bad*.5))
    ind_test[ind_bad[perm[:N_test]]] = True
    ind_err[ind_bad[perm[N_test:]]] = True

    output = {'ind_fit': ind_fit, 'ind_test': ind_test, 'ind_err': ind_err}
    return output


def flags2binflag(flags, reference_flags):
    """
    """

    # The different flags must have same ammount of data.
    N = len(flags[flags.keys()[0]])
    for f in flags:
        assert len(flags[f]) == N

    flags = combined_flag(flags, reference_flags)

    output = ma.masked_all(N, dtype='bool')
    output[flags==1] = True
    output[(flags==3) | (flags==4)] = False

    return output


def order_unprobable_profiles(datadir, varname):
    """ Return a list of profiles ordered by less probable data
    """
    qctests = ['gradient', 'step', 'tukey53H_norm', 'woa_relbias']
    reference_flags = ['global_range', 'gradient_depthconditional',
            'spike_depthconditional', 'digit_roll_over']
    #hardlimit_flags = ['global_range']

    db = ProfilesQCPandasCollection(datadir, saveauxiliary=True)
    aux = db.auxiliary[varname]

    params = fit_tests(aux, qctests, q=.9,)
    prob = estimate_anomaly(aux, params)

    profilename = np.asanyarray(db.data['profilename'])
    output = []
    for pid in np.unique(profilename):
        output.append([pid, min(prob[profilename == pid])])

    return [x[0] for x in sorted(output, key=lambda x: x[1])]


def calibrate_anomaly_detection(datadir, varname):
    """
    """
    qctests = ['gradient', 'step', 'tukey53H_norm', 'woa_relbias']
    reference_flags = ['global_range', 'gradient_depthconditional',
            'spike_depthconditional', 'digit_roll_over']
    #hardlimit_flags = ['global_range']

    db = ProfilesQCPandasCollection(datadir, saveauxiliary=True)
    aux = db.auxiliary[varname]

    binflag = flags2binflag(db.flags[varname], reference_flags)
    # Remove the value out of the possible range.
    ind_outofrange = np.nonzero(db.flags[varname]['global_range'] != 1)
    binflag.mask[ind_outofrange] = True

    result = adjust_anomaly_coefficients(binflag, qctests, aux)

    return result


def human_calibrate_mistakes(datadir, varname, niter=5):
    """
    """
    qctests = ['gradient', 'step', 'tukey53H_norm', 'woa_relbias']
    reference_flags = ['global_range', 'gradient_depthconditional',
            'spike_depthconditional', 'digit_roll_over']
    #hardlimit_flags = ['global_range']

    db = ProfilesQCPandasCollection(datadir, saveauxiliary=True)

    # Remove the value out of the possible range.
    ind_valid = db.flags[varname]['global_range'] == 1
    data = db.data.loc[ind_valid, ['profileid', 'pressure', varname]]
    flags = db.flags[varname][ind_valid]
    aux = db.auxiliary[varname][ind_valid]

    binflag = flags2binflag(flags, reference_flags)

    result = adjust_anomaly_coefficients(binflag, qctests, aux)
    error_log = [{'err': result['err'], 'err_ratio': result['err_ratio'],
                     'p_optimal': result['p_optimal']}]

    # I don't like this approach. Improve this in the future.
    ind_humanqc = binflag.copy()
    for i in range(niter):
        # Profiles with any failure
        mistakes = (result['false_positive'] | result['false_negative'])
        profileids = data['profileid'].iloc[mistakes].unique()
        if len(profileids) == 0:
            break
        # Only 5 profiles each time
        for pid in np.random.permutation(profileids)[:5]:
            print("Profile: %s" % pid)
            ind_p = np.array(data.profileid == pid)
            print data.profilename[ind_p].iloc[0]
            mistakes = (result['false_positive'][ind_p] |
                    result['false_negative'][ind_p])
            h = HumanQC().eval(
                    np.array(data[varname][ind_p]),
                    np.array(data['pressure'][ind_p]),
                    baseflag=ind_humanqc[ind_p],
                    fails=mistakes)#, doubt = ind_doubt[ind])
            ind_humanqc[np.nonzero(ind_p)[0][h=='good']] = True
            ind_humanqc[np.nonzero(ind_p)[0][h=='bad']] = False
            ind_humanqc.mask[np.nonzero(ind_p)[0][h=='doubt']] = True

            result = adjust_anomaly_coefficients(ind_humanqc, qctests, aux)
            error_log.append({'err': result['err'],
                'err_ratio': result['err_ratio'],
                'p_optimal': result['p_optimal']})

        print error_log[-2]
        print error_log[-1]
    return {'ind_humanqc':ind_humanqc, 'error_log': error_log,
            'result': result}
