import os
from os.path import expanduser
import re

import numpy as np
from numpy import ma

try:
    import netCDF4
except:
    print("netCDF4 is not available")

try:
    from pydap.client import open_url
    import pydap.lib
    pydap.lib.CACHE = expanduser('~/.cotederc/pydap_cache')
except:
    print("PyDAP is not available")

from scipy.interpolate import RectBivariateSpline, interp1d

# ============================================================================
def woa_profile(var, d, lat, lon, depth, cfg):
    try:
        woa = woa_profile_from_file(var,
                d, lat, lon, depth, cfg)
    except:
        try:
            woa = woa_profile_from_dap(var,
                d, lat, lon, depth, cfg)
        except:
            print "Couldn't make woa_comparison of %s" % var
            return

    return woa


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
        mn = ma.masked_values(dataset.t_mn.t_mn[dn,:,yn,xn].reshape(dataset['depth'].shape[0]), dataset.t_mn.attributes['_FillValue'])
        sd = ma.masked_values(dataset.t_sd.t_sd[dn,:,yn,xn].reshape(dataset['depth'].shape[0]), dataset.t_sd.attributes['_FillValue'])
        #se = ma.masked_values(dataset.t_se.t_se[dn,:,yn,xn].reshape(dataset['depth'].shape[0]), dataset.t_se.attributes['_FillValue'])
        # Use this in the future. A minimum # of samples
        dd = ma.masked_values(dataset.t_dd.t_dd[dn,:,yn,xn].reshape(dataset['depth'].shape[0]), dataset.t_dd.attributes['_FillValue'])
    elif re.match("salinity\d?$", var):
        mn = ma.masked_values(dataset.s_mn.s_mn[dn,:,yn,xn].reshape(dataset['depth'].shape[0]), dataset.s_mn.attributes['_FillValue'])
        sd = ma.masked_values(dataset.s_sd.s_sd[dn,:,yn,xn].reshape(dataset['depth'].shape[0]), dataset.s_sd.attributes['_FillValue'])
        dd = ma.masked_values(dataset.s_dd.s_dd[dn,:,yn,xn].reshape(dataset['depth'].shape[0]), dataset.s_dd.attributes['_FillValue'])
    zwoa = ma.array(dataset.depth[:])

    ind = (depth<=zwoa.max()) & (depth>=zwoa.min())
    # Mean value profile
    f = interp1d(zwoa[~ma.getmaskarray(mn)].compressed(), mn.compressed())
    mn_interp = ma.masked_all(depth.shape)
    mn_interp[ind] = f(depth[ind])
    # The stdev profile
    f = interp1d(zwoa[~ma.getmaskarray(sd)].compressed(), sd.compressed())
    sd_interp = ma.masked_all(depth.shape)
    sd_interp[ind] = f(depth[ind])

    output = {'woa_an': mn_interp, 'woa_sd': sd_interp}

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
    if lon<0: lon = lon+360

    doy = int(d.strftime('%j'))
    nc = netCDF4.Dataset(expanduser(cfg['file']), 'r')

    # Get the nearest point. In the future interpolate.
    dn = (np.abs(doy - nc.variables['time'][:])).argmin()
    xn = (np.abs(lon - nc.variables['lon'][:])).argmin()
    yn = (np.abs(lat - nc.variables['lat'][:])).argmin()

    vars = cfg['vars']

    climdata = {}
    for v in vars:
        climdata[v] = ma.masked_values(nc.variables[vars[v]][dn, :, yn, xn], nc.variables[vars[v]]._FillValue)

    zwoa = ma.array(nc.variables['depth'][:])

    ind_z = (depth<=zwoa.max()) & (depth>=zwoa.min())
    output = {}
    # Mean value profile
    for v in vars:
        # interp1d can't handle masked values
        ind_valid = ~ma.getmaskarray(climdata[v])
        f = interp1d(zwoa[ind_valid], climdata[v][ind_valid])
        output[v] = ma.masked_all(depth.shape)
        output[v][ind_z] = f(depth[ind_z])
    ## The stdev profile
    #f = interp1d(zwoa[~ma.getmaskarray(sd)].compressed(), sd.compressed())
    #sd_interp = ma.masked_all(depth.shape)
    #sd_interp[ind] = f(depth[ind])

    return output
