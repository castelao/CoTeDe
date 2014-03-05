import numpy as np
from numpy import ma, random
#from scipy.stats import norm, rayleigh, expon, halfnorm, exponpow, exponweib
from scipy.stats import exponweib
#from scipy.stats import kstest

from pydap.client import open_url
import pydap.lib
pydap.lib.CACHE = '.cache'
from scipy.interpolate import RectBivariateSpline, interp1d

# ============================================================================
def get_depth(lat, lon):
    """

    ATENTION, conceptual error on the data near by Greenwich.
    """
    if lat.shape != lon.shape:
        print "lat and lon must have the same size"
    url='http://opendap.ccst.inpe.br/Climatologies/ETOPO/etopo5.cdf'
    dataset = open_url(url)
    etopo = dataset.ROSE
    x = etopo.ETOPO05_X[:]
    if lon.min()<0:
        ind = lon<0
        lon[ind] = lon[ind]+360
    y = etopo.ETOPO05_Y[:]
    iini = max(0, (numpy.absolute(lon.min()-x)).argmin()-2)
    ifin = (numpy.absolute(lon.max()-x)).argmin()+2
    jini = max(0, (numpy.absolute(lat.min()-y)).argmin()-2)
    jfin = (numpy.absolute(lat.max()-y)).argmin()+2
    z = etopo.ROSE[jini:jfin, iini:ifin]
    interpolator = RectBivariateSpline(x[iini:ifin], y[jini:jfin], z.T)
    depth = ma.array([interpolator(xx, yy)[0][0] for xx, yy in zip(lon,lat)])
    return depth

def split_data_groups(ind):
    """ Splits randomly the indices into fit, test and error groups

        Return 3 indices set:
            - ind_fit with 60% of the good
            - ind_test with 20% of the good and 50% of the bad
            - ind_eval with 20% of the good and 50% of the bad
    """
    N = ind.size
    ind_base = np.zeros(N) == 1
    # ==== Good data ==================
    ind_good = np.nonzero((ind == True) & (ma.getmaskarray(ind) == False))[0]
    N_good = ind_good.size
    perm = random.permutation(N_good)
    N_fit = int(round(N_good*.6))
    N_test = int(round(N_good*.2))
    ind_fit = ind_base.copy()
    ind_fit[ind_good[perm[:N_fit]]] = True
    ind_test = ind_base.copy()
    ind_test[ind_good[perm[N_fit:-N_test]]] = True
    ind_err = ind_base.copy()
    ind_err[ind_good[perm[-N_test:]]] = True
    # ==== Bad data ===================
    ind_bad = np.nonzero((ind == False) & (ma.getmaskarray(ind) == False))[0]
    N_bad = ind_bad.size
    perm = random.permutation(N_bad)
    N_test = int(round(N_bad*.5))
    ind_test[ind_bad[perm[:N_test]]] = True
    ind_err[ind_bad[perm[N_test:]]] = True
    output = {'ind_fit': ind_fit, 'ind_test': ind_test, 'ind_err': ind_err}
    return output


# I need to improve this, and include the places where the
#   flags are masked, i.e. only eliminate where the flags
#   could guarantee it was false.

def combined_flag(flags, criteria=None):
    """ Returns the combined flag considering all the criteria

        Collects all flags in the criteria, and for each measurements, it
          return the maximum flag value among the different criteria.

        If criteria is not defined, considers all the flags,
          i.e. flags.keys()
    """
    if criteria is None:
        criteria = flags.keys()

    N = flags[criteria[0]].size
    Nf = len(criteria)
    temp_flag = np.zeros((Nf, N), dtype='i1')
    for i, k in enumerate(criteria):
        temp_flag[i] = flags[k]

    return temp_flag.max(axis=0)

def make_qc_index(flags, criteria, type="anytrue"):
    ind = flags[criteria[0]].copy()
    if type == "anytrue":
        for c in criteria:
            ind[(ind == True) | (flags[c] == True)] = True
        #ind[np.nonzero((ind == True) | (np.array(flags[c]) == True))[0]] = True
    elif type == "alltrue":
        for c in criteria:
            ind[(ind == True) | (flags[c] == True)] = True
    for c in criteria:
        ind[(ind == False) | (flags[c] == False)] = False
        #ind[np.nonzero((ind == False) | (np.array(flags[c]) == False))[0]] = False
    return ind

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

    false_negative = (prob[indices['ind_err']] < p_optimal) & \
        (ind[indices['ind_err']] == True)
    false_positive = (prob[indices['ind_err']] > p_optimal) & \
        (ind[indices['ind_err']] == False)
    err = np.nonzero(false_negative)[0].size + \
            np.nonzero(false_positive)[0].size
    err_ratio = float(err)/prob[indices['ind_err']].size
    false_negative = (prob < p_optimal) & \
        (ind == True)
    false_positive = (prob > p_optimal) & \
        (ind == False)

    output = {'false_negative': false_negative,
            'false_positive': false_positive,
            'prob': prob,
            'p_optimal': p_optimal,
            'err': err,
            'err_ratio': err_ratio,
            'params': params}

    return output
