""" Apply Quality Control of CTD profiles
"""

import pkg_resources
from datetime import datetime

import numpy as np
from numpy import ma

class ProfileQC(object):
    """ Quality Control of a CTD profile
    """
    def __init__(self, data, cfg={}):
        """
            Input: dictionary with data.
                - pressure[\d]:
                - temperature[\d]: 
                - salinity[\d]: 

            cfg: config file with thresholds

            =======================
            - Must have a log system
            - Probably accept incomplete cfg. If some threshold is
                not defined, take the default value.
            - Is the best return another dictionary?
        """

        self.data = data
        self.load_cfg(cfg)
        self.flags = {}

        if 'valid_datetime' in self.cfg['main']:
            self.flags['valid_datetime'] = \
                    type(self.data.attributes['datetime'])==datetime
        if 'at_sea' in self.cfg['main']:
            lon = self.data.attributes['longitude']
            lat = self.data.attributes['latitude']
            if 'url' in self.cfg['main']['at_sea']:
                depth = get_depth_from_DAP(np.array([lat]), 
                        np.array([lon]),
                        url=self.cfg['main']['at_sea']['url'])
                #flag[depth<0] = True
                #flag[depth>0] = False
                #self.flags['at_sea'] = flag
                self.flags['at_sea'] = depth[0]<0

        for v in self.data.keys():
            if v in self.cfg.keys():
                self.test_var(v)

        print self.flags

    def load_cfg(self, cfg):
        """ Load the user's config and the default values

            Need to think better what do I want here. The user
              should be able to choose which variables to evaluate.

            How to handle conflicts between user's cfg and default?
        """
        #defaults = pkg_resources.resource_listdir(__name__, 'defaults')
        self.cfg = eval(pkg_resources.resource_string(__name__, 'defaults'))
        for k in cfg:
            self.cfg[k] = cfg[k]

    def test_var(self, v):

        self.flags[v] = {}
        if 'global_range' in self.cfg[v]:
            f = (self.data[v] >= self.cfg[v]['global_range']['minval']) & (self.data[v] <= self.cfg[v]['global_range']['maxval'])
            self.flags[v]['global_range'] = f

        if 'gradient' in self.cfg[v]:
            threshold = self.cfg[v]['gradient']
            x = self.data[v]
            g = ma.masked_all(x.shape)
            g[1:-1] = np.abs(x[1:-1] - (x[:-2] + x[2:])/2.0)
            flag = ma.masked_all(x.shape, dtype=np.bool)
            flag[np.nonzero(g>threshold)] = False
            flag[np.nonzero(g<=threshold)] = True
            self.flags[v]['gradient'] = flag

        if 'spike' in self.cfg[v]:
            threshold = self.cfg[v]['spike']
            x = self.data[v]
            s = ma.masked_all(x.shape)
            s[1:-1] = np.abs(x[1:-1] - (x[:-2] + x[2:])/2.0) - np.abs((x[2:] - x[:-2])/2.0)
            flag = ma.masked_all(x.shape, dtype=np.bool)
            flag[np.nonzero(s>threshold)] = False
            flag[np.nonzero(s<=threshold)] = True
            self.flags[v]['spike'] = flag

        if 'digit_roll_over' in self.cfg[v]:
            threshold = self.cfg[v]['digit_roll_over']
            x = self.data[v]
            d = ma.masked_all(x.shape)
            step = ma.masked_all(x.shape, dtype=np.float)
            step[1:] = ma.absolute(ma.diff(x))
            flag = ma.masked_all(x.shape, dtype=np.bool)
            flag[ma.absolute(step)>threshold] = False
            flag[ma.absolute(step)<=threshold] = True
            self.flags[v]['digit_roll_over'] = flag

        if 'woa_comparison' in self.cfg[v]:
            import pdb; pdb.set_trace()
            woa = woa_profile_from_dap(v, 
                    int(self.data.attributes['datetime'].strftime('%j')),
                    self.data.attributes['latitude'], 
                    self.data.attributes['longitude'], 
                    self.data['pressure'])
            woa_anom = self.data[v] - woa


def get_depth_from_DAP(lat, lon, url):
    """

    ATENTION, conceptual error on the data near by Greenwich.
    url='http://opendap.ccst.inpe.br/Climatologies/ETOPO/etopo5.cdf'
    """
    from pydap.client import open_url
    import pydap.lib
    pydap.lib.CACHE = '.cache'
    from scipy.interpolate import RectBivariateSpline, interp1d

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
    from pydap.client import open_url
    import pydap.lib
    pydap.lib.CACHE = '.cache'
    from scipy.interpolate import RectBivariateSpline, interp1d
    #import pdb; pdb.set_trace()

    if lon<0: lon = lon+360
    if var == 'temperature':
        url ='http://opendap.ccst.inpe.br/Climatologies/WOA/temperature_monthly_1deg.nc'
    elif var == 'salinity':
        url ='http://opendap.ccst.inpe.br/Climatologies/WOA/salinity_monthly_1deg.nc'
    else:
        return

    dataset = open_url(url)

    dn = (np.abs(doy-dataset['time'][:])).argmin()
    xn = (np.abs(lon-dataset['lon'][:])).argmin()
    yn = (np.abs(lat-dataset['lat'][:])).argmin()

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


