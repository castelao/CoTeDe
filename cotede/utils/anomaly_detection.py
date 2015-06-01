
def fit_tests(aux, qctests, ind=True, q=0.95, verbose=False):
    """
    """
    output = {}
    for teste in qctests:
        samp = aux[teste][ind & np.isfinite(aux[teste])]
        ind_top = samp>samp.quantile(q)
        param = exponweib.fit(samp[ind_top])
        output[teste] = {'param':param,
                'qlimit': samp.quantile(q)}

        if verbose == True:
            import pylab
            x = np.linspace(samp[ind_top].min(), samp[ind_top].max(), 100)
            pdf_fitted = exponweib.pdf(x, *param[:-2], loc=param[-2], scale=param[-1])
            pylab.plot(x,pdf_fitted,'b-')
            pylab.hist(ma.array(samp[ind_top]), 100, normed=1, alpha=.3)
            pylab.title(teste)
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

def adjust_anomaly_coefficients(ind, qctests, aux, q=0.90, verbose=False):
    """ Adjust coeficients for Anomaly Detection, and estimate error

        Inputs:
            ind: Reference index. What the Anomaly Detection will try
                   to reproduce. Uses the True and Falses from ind
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
    indices = split_data_groups(ind)
    params = fit_tests(aux, qctests, indices['ind_fit'], q=q,
            verbose=verbose)
    prob = estimate_anomaly(aux, params)
    if verbose == True:
        pylab.hist(prob); pylab.show()

    p_optimal, test_err = estimate_p_optimal(prob[indices['ind_test']],
            ind[indices['ind_test']])

    # I can extract only .data, since split_data_groups already eliminated
    #   all non valid positions.
    false_negative = (prob[indices['ind_err']] < p_optimal) & \
        (ind[indices['ind_err']].data == True)
    false_positive = (prob[indices['ind_err']] > p_optimal) & \
        (ind[indices['ind_err']].data == False)
    err = np.nonzero(false_negative)[0].size + \
            np.nonzero(false_positive)[0].size
    err_ratio = float(err)/prob[indices['ind_err']].size
    false_negative = (prob < p_optimal) & \
        (ind.data == True) & (ma.getmaskarray(ind)==False)
    false_positive = (prob > p_optimal) & \
        (ind.data == False) & (ma.getmaskarray(ind)==False)

    output = {'false_negative': false_negative,
            'false_positive': false_positive,
            'prob': prob,
            'p_optimal': p_optimal,
            'err': err,
            'err_ratio': err_ratio,
            'params': params}

    return output
