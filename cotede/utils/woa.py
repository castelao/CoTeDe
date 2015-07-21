# -*- coding: utf-8 -*-

from os.path import expanduser
import re
from datetime import datetime

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
from scipy.interpolate import griddata


# ============================================================================
def woa_profile(var, d, lat, lon, depth, cfg):
    # Must improve here. This try make sense if fail because there isn't an
    #   etopo file, but if fail for another reason, like there is no lat,
    #   it will loose time trying from_dap.
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
    if lon < 0:
        lon = lon+360

    url = cfg['url']

    doy = int(d.strftime('%j'))
    dataset = open_url(url)

    dn = (np.abs(doy-dataset['time'][:])).argmin()
    xn = (np.abs(lon-dataset['lon'][:])).argmin()
    yn = (np.abs(lat-dataset['lat'][:])).argmin()

    if re.match("temperature\d?$", var):
        mn = ma.masked_values(dataset.t_mn.t_mn[dn, :, yn, xn].reshape(
            dataset['depth'].shape[0]), dataset.t_mn.attributes['_FillValue'])
        sd = ma.masked_values(dataset.t_sd.t_sd[dn, :, yn, xn].reshape(
            dataset['depth'].shape[0]), dataset.t_sd.attributes['_FillValue'])
        # se = ma.masked_values(dataset.t_se.t_se[dn, :, yn, xn].reshape( dataset['depth'].shape[0]), dataset.t_se.attributes['_FillValue'])
        # Use this in the future. A minimum # of samples
        # dd = ma.masked_values(dataset.t_dd.t_dd[dn, :, yn, xn].reshape(
        #    dataset['depth'].shape[0]), dataset.t_dd.attributes['_FillValue'])
    elif re.match("salinity\d?$", var):
        mn = ma.masked_values(dataset.s_mn.s_mn[dn, :, yn, xn].reshape(
            dataset['depth'].shape[0]), dataset.s_mn.attributes['_FillValue'])
        sd = ma.masked_values(dataset.s_sd.s_sd[dn, :, yn, xn].reshape(
            dataset['depth'].shape[0]), dataset.s_sd.attributes['_FillValue'])
        # dd = ma.masked_values(dataset.s_dd.s_dd[dn, :, yn, xn].reshape(
        #    dataset['depth'].shape[0]), dataset.s_dd.attributes['_FillValue'])
    zwoa = ma.array(dataset.depth[:])

    ind = (depth <= zwoa.max()) & (depth >= zwoa.min())
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
    if lon < 0:
        lon = lon + 360

    doy = int(d.strftime('%j'))
    nc = netCDF4.Dataset(expanduser(cfg['file']), 'r')

    # Get the nearest point. In the future interpolate.
    dn = (np.abs(doy - nc.variables['time'][:])).argmin()
    xn = (np.abs(lon - nc.variables['lon'][:])).argmin()
    yn = (np.abs(lat - nc.variables['lat'][:])).argmin()

    vars = cfg['vars']

    climdata = {}
    for v in vars:
        climdata[v] = ma.masked_values(
                nc.variables[vars[v]][dn, :, yn, xn],
                nc.variables[vars[v]]._FillValue)

    zwoa = ma.array(nc.variables['depth'][:])

    ind_z = (depth <= zwoa.max()) & (depth >= zwoa.min())
    output = {}
    # Mean value profile
    for v in vars:
        # interp1d can't handle masked values
        ind_valid = ~ma.getmaskarray(climdata[v])
        f = interp1d(zwoa[ind_valid], climdata[v][ind_valid])
        output[v] = ma.masked_all(depth.shape)
        output[v][ind_z] = f(depth[ind_z])
    # # The stdev profile
    # f = interp1d(zwoa[~ma.getmaskarray(sd)].compressed(), sd.compressed())
    # sd_interp = ma.masked_all(depth.shape)
    # sd_interp[ind] = f(depth[ind])

    return output


def woa_track_from_file(d, lat, lon, filename, varnames=None):
    """ Temporary solution: WOA for surface track
    """
    d = np.asanyarray(d)
    lat = np.asanyarray(lat)
    lon = np.asanyarray(lon)

    lon[lon<0] += 360

    doy = np.array([int(dd.strftime('%j')) for dd in d])

    nc = netCDF4.Dataset(expanduser(filename), 'r')

    if varnames is None:
        varnames = {}
        for v in nc.variables.keys():
            if nc.variables[v].dimensions == (u'time', u'depth', u'lat', u'lon'):
                varnames[v] = v

    output = {}
    for v in varnames:
        output[v] = []

    for d_n, lat_n, lon_n in zip(doy, lat, lon):
        # Get the nearest point. In the future interpolate.
        n_d = (np.abs(d_n- nc.variables['time'][:])).argmin()
        n_x = (np.abs(lon_n - nc.variables['lon'][:])).argmin()
        n_y = (np.abs(lat_n - nc.variables['lat'][:])).argmin()

        for v in varnames:
            output[v].append(nc.variables[varnames[v]][n_d, 0, n_y, n_x])

    for v in varnames:
        output[v] = ma.fix_invalid(output[v])

    return output

# ---- unifinished, under development ----
def build_input(doy, depth, lat, lon, filename, varnames):
    """ Subsample WOA from nc file

        To improve efficiency of interpolation
    """
    nc = netCDF4.Dataset(expanduser(filename), 'r')

    output = {}
    for v in (u'time', u'depth', u'lat', u'lon'):
        output[v] = nc.variables[v][:]
    for v in varnames:
        output[v] = nc.variables[v][:]

    return output
    # Get the nearest point. In the future interpolate.
    dn = slice(
            (np.abs(np.min(doy) - nc.variables['time'][:])).argmin() - 1,
            (np.abs(np.max(doy) - nc.variables['time'][:])).argmin() + 1
            )
    zn = slice(
            (np.abs(np.min(depth) - nc.variables['depth'][:])).argmin() - 1,
            (np.abs(np.max(depth) - nc.variables['depth'][:])).argmin() + 1
            )
    xn = slice(
            (np.abs(np.min(lon) - nc.variables['lon'][:])).argmin() - 1,
            (np.abs(np.max(lon) - nc.variables['lon'][:])).argmin() + 1
            )
    yn = slice(
            (np.abs(np.min(lat) - nc.variables['lat'][:])).argmin() - 1,
            (np.abs(np.max(lat) - nc.variables['lat'][:])).argmin() + 1
            )

    # Temporary solution. Improve in the future
    if dn.start < 0:
        dn = slice(0, dn.stop, dn.step)
    if zn.start < 0:
        zn = slice(0, zn.stop, zn.step)
    if xn.start < 0:
        xn = slice(0, xn.stop, xn.step)
    if yn.start < 0:
        yn = slice(0, yn.stop, yn.step)


def woa_from_file(doy, depth, lat, lon, filename, varnames=None):
    """
    Monthly Climatologic Mean and Standard Deviation from WOA,
    used either for temperature or salinity.

    INPUTS
        doy: [day of year]
        lat: [-90<lat<90]
        lon: [-180<lon<180]
        depth: [meters]

    Reads the WOA Monthly Climatology NetCDF file and
    returns the corresponding WOA values of salinity or temperature mean and
    standard deviation for the given time, lat, lon, depth.
    """

    doy = np.asanyarray(doy)
    depth = np.asanyarray(depth)
    lat = np.asanyarray(lat)
    lon = np.asanyarray(lon)

    assert np.all(depth >= 0)

    if lon < 0:
        lon = lon + 360

    nc = netCDF4.Dataset(expanduser(filename), 'r')

    if varnames is None:
        varnames = []
        for v in nc.variables.keys():
            if nc.variables[v].dimensions == (u'time', u'depth', u'lat', u'lon'):
                varnames.append(v)

    woa = build_input(doy, depth, lat, lon, filename, varnames)

    points_out = []
    for tn in doy:
        for zn in depth:
            for yn in lat:
                for xn in lon:
                    points_out.append([tn, zn, yn, xn])

    import pdb; pdb.set_trace()
    output = []
    for v in varnames:
        values = []
        points = []
        ind = np.nonzero(~ma.getmaskarray(woa[v]))
        points = np.array([
            woa['time'][ind[0]],
            woa['depth'][ind[0]],
            woa['lat'][ind[0]],
            woa['lon'][ind[0]]
            ]).T
        values = woa[v][ind]

        for nt, tn in enumerate(woa['time']):
            for nz, zn in enumerate(woa['depth']):
                for ny, yn in enumerate(woa['lat']):
                    for nx, xn in enumerate(woa['lon']):
                        points.append([tn, zn, yn, xn])
                        values.append(woa[v][nt, nz, ny, nx])
        points = np.array(points)
        values = np.array(points)
        output[v] = griddata(points, values, points_out)

    return output
