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
