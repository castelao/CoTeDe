# -*- coding: utf-8 -*-

"""


Target: Initially two main functionalities

- Quality control flagging
    - Input:
        - Lista de arquivo | diretório
        - Q.C. config (can be a file)
        - Features (just varnames)
    - Pandas Collection:
        - Load all files and return flags plus features (aux)
    - Split groups: fit, test, eval
    - Calibrate:
        - Fit PDF parameters for each feature using fit group
        - Define the optimal thresholds comparing with flags from Q.C. config
            - There is the possibility to human interaction to overwrite the flags from the auto Q.C.
        - Estimate the error
        - The threshold between good or bad flags were defined on the second step, but now consider the whole dataset. The highest probability of any bad value is the thresholds between 1 and 2. In other words, all data with higher probability that this threshold where good. Between this threshold and the optimal previously defined there were bad data, but it was mostly good ones, hence flag 2 which means probably good. With the same concept define the threshold between flags 3 and 4.

    With the coeficients determined, an independent procedure to flag all data. Independent because the anomaly detection flagging itself can simply be loaded by previsouly defined coeficients, hence start already from this point.
    - Fit features, on full DB, there is no split data
    - With the parameters on the previous step estimate the probability of each measurement
    - Create a list sorted by:
        - Produtorium of all probabilities or,
        - Min(P(x_i)), the lowest probability for each measurement
    - The output would be a list to feed the Human Q.C. system
"""

import numpy as np
from numpy import ma
# from scipy.stats import norm, rayleigh, expon, halfnorm, exponpow, exponweib
from scipy.stats import exponweib
# from scipy.stats import kstest

from cotede.misc import combined_flag
from cotede.humanqc import HumanQC


def fit_tests(features, q=0.90, verbose=False):
    """

        Input:
          features: a dictionary like with the numerical results from the
              QC tests. For example, the gradient test values, not the
              flags, but the floats itself, like
              {'gradient': ma.array([.23, .12, .08]), 'spike': ...}
              It also works with a pandas.DataFrame()

          q: The lowest percentile to be considered. For example, .90
              means that only the top 10% data (i.e. percentiles higher
              than .90) are considered in the fitting.
    """
    assert (q >= 0) & (q < 1), "q must be in [0, 1)"

    output = {}
    for f in features:
        # Sample only valid values
        samp = ma.compressed(features[f][np.isfinite(features[f])])
        # Identify the percentile q
        qlimit = np.percentile(samp, 1e2*q)
        # Restricts to the top q values
        samp = samp[samp > qlimit]
        if samp.any():
            param = exponweib.fit(samp)
            output[f] = {'param': param,
                    'qlimit': qlimit}

        if verbose is True:
            import pylab
            x = np.linspace(samp.min(), samp.max(), 100)
            pdf_fitted = exponweib.pdf(x, *param[:-2], loc=param[-2], scale=param[-1])
            pylab.plot(x, pdf_fitted, 'b-')
            pylab.hist(ma.array(samp), 100, normed=1, alpha=.3)
            pylab.title(f)
            pylab.show()

    return output


def estimate_anomaly(features, params, method='produtorium'):
    """ Estimate probability from PDF defined by params

        The output is the natural logarithm of the estimated probability.

        params are the parameters that define the PDF for each feature
          in features. This function estimate the combined probability of
          each row in features as the produtorium between the probabilities
          of the different features on the same row.

        ATENTION!! I should think more about what would I like from this
          function. What should happens in case of a masked feature? And
          if all features for one measurement are masked? Right now it
          simply don't add for the estimate, so that all features masked
          would lead to an expectation of 100% it's good.
    """
    assert hasattr(params, 'keys')
    assert hasattr(features, 'keys')

    features_names = list(features.keys())
    for k in params.keys():
        assert k in features_names, "features doesn't have: %s" % k

    prob = ma.masked_all(np.shape(features[features_names[0]]), dtype='f8')

    for t in params.keys():
        param = params[t]['param']
        valid = ~ma.fix_invalid(features[t]).mask

        tmp = exponweib.sf(np.asanyarray(features[t]),
                *param[:-2], loc=param[-2], scale=param[-1])
        # Arbitrary solution. No value can have a probability of 0.
        tmp[tmp == 0] = 1e-25
        p = ma.log(tmp)

        # If both are valid, operate as choosed method.
        ind = ~prob.mask & valid
        if method == 'produtorium':
            prob[ind] = prob[ind] + p[ind]
        elif method == 'min':
            prob[ind] = min(prob[ind], p[ind])
        else:
            assert "Invalid method: %s" % method

        # Update prob if new value is valid and prob is masked
        # Operate twice the first feature if moved above.
        ind = prob.mask & valid
        prob[ind] = p[ind]

    return prob


def estimate_p_optimal(prob, binflag, verbose=False):
    """ ATENTION: I'm not happy with this. Improve it

        Maybe use flag as input, and optimize to give 3 thresholds
    """
    assert prob.shape == binflag.shape
    assert binflag.dtype == 'bool'

    err = []
    p_limit = prob[np.nonzero(binflag)].min() - 0.1
    P = -np.arange(0, -p_limit, 0.1)
    N = P.size
    err = np.empty(N)
    false_negative = np.empty(N)
    false_positive = np.empty(N)
    for i, p in enumerate(P):
        # The nonzero is necessary in case binflag is a masked array.
        false_negative[i] = np.nonzero(prob[np.nonzero(binflag)] < p)[0].size
        false_positive[i] = np.nonzero(prob[np.nonzero(~binflag)] > p)[0].size
        err[i] = false_negative[i] + false_positive[i]

    if verbose is True:
        import pylab
        pylab.plot(P, err , 'b'); pylab.show()

    return P[err.argmin()], float(err.min())/prob.size#, {'P': P, 'err': err}


def calibrate4flags(flags, features, q=0.90, verbose=False):
    """ Adjust coeficients for Anomaly Detection to best reproduce given flags

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
    assert hasattr(features, 'keys')

    binflags = i2b_flags(flags)
    assert len(features[features.keys()[0]]) == len(binflags)

    indices = split_data_groups(binflags)
    params = fit_tests(features[indices['fit']], q=q)
    prob = estimate_anomaly(features, params)

    if verbose is True:
        pylab.hist(prob)
        pylab.show()

    p_optimal, test_err = estimate_p_optimal(prob[indices['test']],
            binflags[indices['test']])

    # Guarantee the the false_* indices will be np.array
    false_negative = (prob < p_optimal) & binflags
    false_negative[ma.getmaskarray(false_negative)] = False
    false_negative = np.array(false_negative)
    false_positive = (prob > p_optimal) & ~binflags
    false_positive[ma.getmaskarray(false_positive)] = False
    false_positive = np.array(false_positive)

    mistake = false_positive | false_negative

    # I can extract only .data, since split_data_groups already eliminated
    #   all non valid positions.
    #err = np.nonzero(false_negative)[0].size + \
    #        np.nonzero(false_positive)[0].size
    tot_misfit = np.nonzero(mistake)[0].size
    n_err = float(np.nonzero(mistake[indices['err']])[0].shape[0])
    #err_ratio = float(err)/prob[indices['ind_err']].size
    err_ratio = n_err/indices['err'].astype('i').sum()
    #false_negative = (prob < p_optimal) & \
    #    (flag_ref.data is True) & (ma.getmaskarray(flag_ref) is False)
    #false_positive = (prob > p_optimal) & \
    #    (flag_ref.data is False) & (ma.getmaskarray(flag_ref) is False)

    output = {'false_negative': false_negative,
            'false_positive': false_positive,
            'prob': prob,
            'p_optimal': p_optimal,
            'tot_misfit': tot_misfit,
            'n_err': n_err,
            'err_ratio': err_ratio,
            'params': params}

    return output


def split_data_groups(flag):
    """ Splits randomly the indices into fit, test and error groups

        Return a dictionary with 3 indices set:
            - ind_fit with 60% of the good
            - ind_test with 20% of the good and 50% of the bad
            - ind_eval with 20% of the good and 50% of the bad
    """
    assert flag.dtype == 'bool'

    N = flag.size
    ind_base = np.zeros(N) == 1
    ind_valid = ~ma.getmaskarray(flag)

    # ==== Good data ==================
    ind_good = np.nonzero((flag == True)  & ind_valid)[0]
    N_good = ind_good.size
    perm = np.random.permutation(N_good)
    N_test = int(round(N_good*.2))
    ind_test = ind_base.copy()
    ind_test[ind_good[perm[:N_test]]] = True
    ind_err = ind_base.copy()
    ind_err[ind_good[perm[N_test:2*N_test]]] = True
    ind_fit = ind_base.copy()
    ind_fit[ind_good[perm[2*N_test:]]] = True

    # ==== Bad data ===================
    ind_bad = np.nonzero((flag == False) & ind_valid)[0]
    N_bad = ind_bad.size
    perm = np.random.permutation(N_bad)
    N_test = int(round(N_bad*.5))
    ind_test[ind_bad[perm[:N_test]]] = True
    ind_err[ind_bad[perm[N_test:]]] = True

    return {'fit': ind_fit, 'test': ind_test, 'err': ind_err}


def i2b_flags(flags, good_flags=[1,2], bad_flags=[3,4]):
    """ Converts int flags (like IOC) into binary (T|F)

        If given a dictionary of flags, it will evaluate each item
          of the dictionary, and return:
          - True if all available values are True
          - False if any of the available values is False
          - Masked is all values are masked
    """

    if (hasattr(flags, 'keys')) and (np.ndim(flags) > 1):
        output= []
        for f in flags:
            output.append(i2b_flags(flags[f], good_flags, bad_flags))

        return ma.array(output).all(axis=0)

    flags = np.asanyarray(flags)
    assert flags.dtype != 'bool', "Input flags should not be binary"
    output = ma.masked_all(np.shape(flags), dtype='bool')

    for f in good_flags:
        output[flags == f] = True
    for f in bad_flags:
        output[flags == f] = False

    return output


def calibrate_anomaly_detection(datadir, varname, cfg=None):
    """ Calibrate coefficientes for Anomaly Detection

        Input:
            datadir: Directory with the data to be used on calibration
            varname: Variable to calibrate. For example: TEMP
            cfg: CoTeDe's QC configuration. Can be None for CoTeDe's default
                a name for one of the preset configuration files, or a dict

        Output:
            false_negative:
            false_positive:
            prob:
            p_optimal:
            err:
            err_ratio:
            params:

        Loads all the data in datadir, apply the Q.C. procedures according to
          cfg, and than calibrate params and p_optimal so that anomaly
          detection reproduces the combined flags from the Q.C.
    """
    import pandas as pd

    assert type(varname) is str, "varname must be a string"

    db = ProfilesQCPandasCollection(datadir, cfg=cfg, saveauxiliary=True)

    assert varname in db.keys(), "db does not contain variable %s" % varname

    # # Remove the value out of the possible range.
    # ind_outofrange = np.nonzero(db.flags[varname]['global_range'] != 1)
    # binflag.mask[ind_outofrange] = True
    # hardlimit_flags = ['global_range']
    ind = db.flags[varname]['global_range'] == 1
    #aux = db.auxiliary[varname][ind]
    #features = aux.drop(['id','profileid'], axis=1)
    features = db.auxiliary[varname][ind]
    #flags = db.flags[varname][ind].drop(['id','profileid', 'density_inversion'], axis=1)
    #flags = db.flags[varname][ind].drop(['density_inversion'], axis=1)
    #flags = combined_flag(flags)
    #flags = combined_flag(db.flags[varname][ind])
    #binflags = i2b_flags(flags)

    result = calibrate4flags(db.flags[varname][ind],
            db.auxiliary[varname][ind], q=0.90, verbose=False)

    #ind = ma.masked_all(len(flags), dtype='bool')
    #ind[(flags == 1) | (flags == 2)] = True
    #ind[(flags == 3) | (flags == 4)] = False
    #indices = split_data_groups(ind)
    #indices = split_data_groups(flags)


    #params = fit_tests(features[indices['fit']], q=.9)
    #prob = estimate_anomaly(features, params)

    #binflag = i2b_flagsflag(db.flags[varname][ind], reference_flags)

    #p_optimal, test_err = estimate_p_optimal(prob[indices['test']],
    #        i2b_flags(flags[indices['test']]))

    #false_negative = prob[indices['err'] & binflags] < p_optimal
    #false_positive = prob[indices['err'] & ~binflags] < p_optimal
    #err = np.nonzero(false_negative)[0].size + \
    #        np.nonzero(false_positive)[0].size
    #err_ratio = float(err)/prob[indices['err']].size

    #output = {'false_negative': false_negative,
    #        'false_positive': false_positive,
    #        'prob': prob,
    #        'p_optimal': p_optimal,
    #        'err': err,
    #        'err_ratio': err_ratio,
    #        'params': params}

    #result = adjust_anomaly_coefficients(binflag, qctests, aux)

    #return output
    return result


def human_calibrate_mistakes(data, varname, flagname, featuresnames, niter=5):
    """
    """
    q = 0.90
    assert varname in data

    import pandas as pd
    #data['id'] = range(data.shape[0])
    #data.set_index('id', drop=True, inplace=True)
    # Guarantee that the indices are unique.
    assert data.index.unique().shape[0] == data.shape[0]

    if 'human_flag' not in data:
        data['human_flag'] = ma.masked_all(data[flagname].shape,
                dtype='object')
    data['flag_calibrating'] = data[flagname].copy()
    data.loc[data.human_flag == 'good', 'flag_calibrating'] = 1
    data.loc[data.human_flag == 'bad', 'flag_calibrating'] = 4

    result = calibrate4flags(data['flag_calibrating'], data[featuresnames], q=q)

    error_log = [{'err': result['n_err'],
        'err_ratio': result['err_ratio'],
        'p_optimal': result['p_optimal']}]

    for i in range(niter):
        for v in ['false_positive', 'false_negative', 'prob']:
            data[v] = result[v]
        # Failures from AD to reproduce flags
        data['mistake'] = data['human_flag'].isnull() & \
                (data['false_positive'] | data['false_negative'])

        # AD's severity error is given by how far away was the estimated
        #   probability from the prob. threshold.
        data['derr'] = (data.prob - result['p_optimal']).abs()
        data.loc[data.mistake == False, 'derr'] = np.nan

        grp = data[data.mistake].groupby('profileid')
        profileids = grp['derr'].max().sort_values(ascending=False).index

        # In the future order by how badly AD mistaked
        if len(profileids) == 0:
            break
        # 5 random profiles with mistakes
        # for pid in profileids[:10]:
        for pid in np.random.permutation(profileids[:10])[:5]:
            print("Profile: %s" % pid)
            profile = data[data.profileid == pid]
            h = HumanQC().eval(
                    profile[varname],
                    profile['PRES'],
                    baseflag=profile['flag_calibrating'],
                    #fails=np.array(profile['mistake']),
                    #fails=ma.array(profile.derr == profile.loc[
                    #    profile.flag_global_range == 1, 'derr'].max()),
                    fails=np.array(profile.derr == profile.derr.max()),
                    humanflag=ma.masked_values(
                        profile['human_flag'], None).astype('object'))

            # Update human_flag only at the new values
            profile.loc[:, 'human_flag'] = h
            for i in profile.index[profile.human_flag.notnull()]:
                data.loc[i, 'human_flag'] = profile.loc[i, 'human_flag']

        data.loc[data.human_flag == 'good', 'flag_calibrating'] = 1
        data.loc[data.human_flag == 'bad', 'flag_calibrating'] = 4
        data.loc[data.human_flag == 'doubt', 'flag_calibrating'] = 0

        result = calibrate4flags(data['flag_calibrating'], data[featuresnames], q=q)


        error_log.append({'err': result['n_err'],
            'err_ratio': result['err_ratio'],
            'p_optimal': result['p_optimal'],
            'tot_misfit': result['tot_misfit']})

        print(error_log[-2])
        print(error_log[-1])

    result['human_flag'] = data['human_flag']
    result['error_log'] = error_log

    return result


def rank_files(datadir, varname, cfg=None):
    """
        Ordered list from datadir files of probably bad data


        The concept is for a recommendation system for Human Q.C.

            - Input: Lista de arquivo | diretório
            - Pandas Collection:
                - Load all files and return flags plus features (aux)
            - Fit features, on full DB, there is no split data
            - With the parameters on the previous step estimate the
                probability of each measurement
            - Create a list sorted by:
                - Produtorium of all probabilities or,
                - Min(P(x_i)), the lowest probability for each measurement
            - The output would be a list to feed the Human Q.C. system

        ATENTION: I must create some tests for this function.
    """
    import pandas as pd

    assert type(varname) is str

    db = ProfilesQCPandasCollection(datadir, cfg=cfg, saveauxiliary=True)

    # hardlimit_flags = ['global_range']
    ind = db.flags[varname]['global_range'] == 1
    features = db.auxiliary[varname][ind]

    params = fit_tests(features, q=.85)
    # Note that I'm already filtering to positions ind, i.e. valid
    #   global range limits. Global range is too obvious and should
    #   be left aside.
    prob = estimate_anomaly(features, params)

    tmp = db.data.loc[ind, ['profilename']]
    tmp.loc[:, 'anomaly_detection'] = pd.Series(prob, index=tmp.index)
    grp = tmp.groupby('profilename')
    output = grp.min().sort_values(by='anomaly_detection').index.tolist()

    return output

    # profilename = np.asanyarray(db.data['profilename'])
    # output = []
    # for pid in np.unique(profilename):
    #     output.append([pid, min(prob[profilename == pid])])

    # return [x[0] for x in sorted(output, key=lambda x: x[1])]
