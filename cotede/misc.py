import numpy as np
from numpy import ma, random

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

def woa_profile_from_dap(var, doy, lat, lon, depth):
    """
    Monthly Climatologic Mean and Standard Deviation from WOA,
    used either for temperature or salinity.

    INPUTS
        time: [day of the year]
        lat: [-90<lat<90]
        lon: [-180<lon<180]
        depth: [meters]

    Reads the WOA Monthly Climatology NetCDF file and
    returns the corresponding WOA values of salinity or temperature mean and
    standard deviation for the given time, lat, lon, depth.
    """
    if lon<0: lon = lon+360
    if var == 'temperature':
        url ='http://opendap.ccst.inpe.br/Climatologies/WOA/temperature_monthly_1deg.nc'
    elif var == 'salinity':
        url ='http://opendap.ccst.inpe.br/Climatologies/WOA/salinity_monthly_1deg.nc'
    else:
        return

    dataset = open_url(url)

    dn = (numpy.abs(doy-dataset['time'][:])).argmin()
    xn = (numpy.abs(lon-dataset['lon'][:])).argmin()
    yn = (numpy.abs(lat-dataset['lat'][:])).argmin()

    data = {}
    if var == 'temperature':
        an = ma.masked_values(dataset.t_an.t_an[dn,:,yn,xn].reshape(dataset['depth'].shape[0]), dataset.t_an.attributes['_FillValue'])
        #sd = ma.masked_values(dataset.t_sd.t_sd[dn,:,yn,xn].reshape(dataset['depth'].shape[0]), dataset.t_sd.attributes['_FillValue'])
        #se = ma.masked_values(dataset.t_se.t_se[dn,:,yn,xn].reshape(dataset['depth'].shape[0]), dataset.t_se.attributes['_FillValue'])
        #dd = ma.masked_values(dataset.t_dd.t_dd[dn,:,yn,xn].reshape(dataset['depth'].shape[0]), dataset.t_dd.attributes['_FillValue'])
    elif var == 'salinity':
        an = ma.masked_values(dataset.s_an.s_an[dn,:,yn,xn].reshape(dataset['depth'].shape[0]), dataset.s_an.attributes['_FillValue'])
        #sd = ma.masked_values(dataset.s_sd.s_sd[dn,:,yn,xn].reshape(dataset['depth'].shape[0]), dataset.s_sd.attributes['_FillValue'])
    zwoa = ma.array(dataset.depth[:])

    ind=depth<=zwoa.max()
    # Mean value profile
    f = interp1d(zwoa[~ma.getmaskarray(an)].compressed(), an.compressed())
    an_interp = ma.masked_all(depth.shape)
    an_interp[ind] = f(depth[ind])
    # The stdev profile
    #f = interp1d(zwoa[~ma.getmaskarray(sd)].compressed(), sd.compressed())
    #sd_interp = ma.masked_all(depth.shape)
    #sd_interp[ind] = f(depth[ind])

    #return an_interp, sd_interp
    return an_interp


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
    ind_good = np.nonzero(ind == True)[0]
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
    ind_bad = np.nonzero(ind == False)[0]
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
        samp = aux[teste][ind]
        ind_top = samp>samp.quantile(q)
        param = exponweib.fit(samp[ind_top])
        output[teste] = {'param':param,
                'q95': samp.quantile(q)}

        if verbose == True:
            x = linspace(samp[ind_top].min(), samp[ind_top].max(), 100)[1:]
            pdf_fitted = exponweib.pdf(x, *param[:-2], loc=param[-2], scale=param[-1])
            pylab.plot(x,pdf_fitted,'b-')
            pylab.hist(samp[ind_top], 100, normed=1,alpha=.3)
            pylab.title(teste)
            pylab.show()

    return output

def estimate_anomaly(aux):
    prob = ma.ones(aux.shape[0])
    for t in output.keys():
        param = output[t]['param']
        ind = np.isfinite(aux[t])
        prob[ind] = prob[ind] * \
                exponweib.sf(aux[t][ind], *param[:-2], loc=param[-2], scale=param[-1])
    return prob
