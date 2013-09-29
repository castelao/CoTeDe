import re
import glob

import numpy as np
from numpy import ma

from pydap.client import open_url
import pydap.lib
pydap.lib.CACHE = '.cache'
from scipy.interpolate import RectBivariateSpline, interp1d

def make_file_list(inputdir, inputpattern):
    """
    """
    inputfiles = glob.glob(inputdir + inputpattern)
    inputfiles.sort()

    return inputfiles

def get_depth_from_DAP(lat, lon, url):
    """

    ATENTION, conceptual error on the data near by Greenwich.
    url='http://opendap.ccst.inpe.br/Climatologies/ETOPO/etopo5.cdf'
    """

    if lat.shape != lon.shape:
                print "lat and lon must have the same size"
    dataset = open_url(url)
    etopo = dataset.ROSE
    x = etopo.ETOPO05_X[:]
    if lon.min()<0:
        ind = lon<0
        lon[ind] = lon[ind]+360
    y = etopo.ETOPO05_Y[:]
    iini = max(0, (np.absolute(lon.min()-x)).argmin()-2)
    ifin = (np.absolute(lon.max()-x)).argmin()+2
    jini = max(0, (np.absolute(lat.min()-y)).argmin()-2)
    jfin = (np.absolute(lat.max()-y)).argmin()+2
    z = etopo.ROSE[jini:jfin, iini:ifin]
    interpolator = RectBivariateSpline(x[iini:ifin], y[jini:jfin], z.T)
    depth = ma.array([interpolator(xx, yy)[0][0] for xx, yy in zip(lon,lat)])
    return depth

# ============================================================================
def woa_profile_from_dap(var, d, lat, lon, depth, cfg):
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

    url = cfg['url']

    doy = int(d.strftime('%j'))
    dataset = open_url(url)

    dn = (np.abs(doy-dataset['time'][:])).argmin()
    xn = (np.abs(lon-dataset['lon'][:])).argmin()
    yn = (np.abs(lat-dataset['lat'][:])).argmin()

    if re.match("temperature\d?$", var):
        an = ma.masked_values(dataset.t_an.t_an[dn,:,yn,xn].reshape(dataset['depth'].shape[0]), dataset.t_an.attributes['_FillValue'])
        sd = ma.masked_values(dataset.t_sd.t_sd[dn,:,yn,xn].reshape(dataset['depth'].shape[0]), dataset.t_sd.attributes['_FillValue'])
        #se = ma.masked_values(dataset.t_se.t_se[dn,:,yn,xn].reshape(dataset['depth'].shape[0]), dataset.t_se.attributes['_FillValue'])
        # Use this in the future. A minimum # of samples
        #dd = ma.masked_values(dataset.t_dd.t_dd[dn,:,yn,xn].reshape(dataset['depth'].shape[0]), dataset.t_dd.attributes['_FillValue'])
    elif re.match("salinity\d?$", var):
        an = ma.masked_values(dataset.s_an.s_an[dn,:,yn,xn].reshape(dataset['depth'].shape[0]), dataset.s_an.attributes['_FillValue'])
        sd = ma.masked_values(dataset.s_sd.s_sd[dn,:,yn,xn].reshape(dataset['depth'].shape[0]), dataset.s_sd.attributes['_FillValue'])
        #dd = ma.masked_values(dataset.s_dd.s_dd[dn,:,yn,xn].reshape(dataset['depth'].shape[0]), dataset.s_dd.attributes['_FillValue'])
    zwoa = ma.array(dataset.depth[:])

    ind=depth<=zwoa.max()
    # Mean value profile
    f = interp1d(zwoa[~ma.getmaskarray(an)].compressed(), an.compressed())
    an_interp = ma.masked_all(depth.shape)
    an_interp[ind] = f(depth[ind])
    # The stdev profile
    f = interp1d(zwoa[~ma.getmaskarray(sd)].compressed(), sd.compressed())
    sd_interp = ma.masked_all(depth.shape)
    sd_interp[ind] = f(depth[ind])

    output = {'woa_an': an_interp, 'woa_sd': sd_interp}

    return output

# ============================================================================
def woa_profile_from_file(var, d, lat, lon, depth, cfg):
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
    from netCDF4 import Dataset
    if lon<0: lon = lon+360

    doy = int(d.strftime('%j'))
    nc = Dataset(cfg['file'], 'r')

    # Get the nearest point. In the future interpolate.
    dn = (np.abs(doy - nc.variables['time'][:])).argmin()
    xn = (np.abs(lon - nc.variables['lon'][:])).argmin()
    yn = (np.abs(lat - nc.variables['lat'][:])).argmin()

    vars = cfg['vars']

    climdata = {}
    for v in vars:
        climdata[v] = ma.masked_values(nc.variables[vars[v]][dn, :, yn, xn], nc.variables[vars[v]]._FillValue)

    zwoa = ma.array(nc.variables['depth'][:])

    ind = (depth<=zwoa.max()) & (depth>=zwoa.min())
    output = {}
    # Mean value profile
    for v in vars:
        f = interp1d(zwoa, climdata[v])
        output[v] = ma.masked_all(depth.shape)
        output[v][ind] = f(depth[ind])
    ## The stdev profile
    #f = interp1d(zwoa[~ma.getmaskarray(sd)].compressed(), sd.compressed())
    #sd_interp = ma.masked_all(depth.shape)
    #sd_interp[ind] = f(depth[ind])

    return output
