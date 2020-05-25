# -*- coding: utf-8 -*-

"""


    Create a test to check if cfg['vars'] does exist in the climatology file,
      to avoid error like have t_mn in one and t_an in the other.

    An idea to improve the climatology test. Gridpoints estimated from few
      measurements should be less trustable. Here I'm using a threshold of at
      least 3 samples to be considered. Deep ocean is in general quite
      stable, so few measurements should be sufficient. One possibility is to
      estimate the standard error, which depends on the ammount of samples and
      estimated standard deviation. This would be the 'uncertainty on the
      estimated average climatology. Any measurement in that range would be
      considered statistically identical to the climatology. Above that
      difference, it would be normalized by the standard deviation. Therefore,
      stable areas would be less tolerant to variability, even with few samples.
"""

from datetime import timedelta
import logging

import numpy as np
from numpy import ma
from oceansdb import WOA

from .qctests import QCCheckVar

module_logger = logging.getLogger(__name__)


def woa_normbias(data, v, cfg):
    """

        FIXME: Move this procedure into a class to conform with the new system
          and include a limit in minimum ammount of samples to trust it. For
          example, consider as masked all climatologic values estimated from
          less than 5 samples.
    """

    # 3 is the possible minimum to estimate the std, but I shold use higher.
    min_samples = 3
    woa = None

    db = WOA()
    if v not in db.keys():
        vtype = v[:-1]
    else:
        vtype = v

    # Temporary solution while I'm not ready to handle tracks.
    if ('LATITUDE' in data) and ('LONGITUDE' in data) \
            and ('LATITUDE' not in data.attributes) \
            and ('LONGITUDE' not in data.attributes):
        if 'datetime' in data.keys():
            d = data['datetime']
        elif ('datetime' in data.attributes):
            d0 = data.attributes['datetime']
            if ('timeS' in data.keys()):
                d = [d0 + timedelta(seconds=s) for s in data['timeS']]
            else:
                d = [data.attributes['datetime']]*len(data['LATITUDE']),

        #woa = woa_track_from_file(
        #        d,
        #        data['LATITUDE'],
        #        data['LONGITUDE'],
        #        cfg['file'],
        #        varnames=cfg['vars'])

        module_logger.error("Sorry, I'm temporary not ready to handle tracks.")
        #woa = db[vtype].get_track(var=['mean', 'standard_deviation'],
        #        doy=d,
        #        depth=[0],
        #        lat=data['LATITUDE'],
        #        lon=data['LONGITUDE'])

    elif ('LATITUDE' in data.attributes.keys()) and \
            ('LONGITUDE' in data.attributes.keys()) and \
            ('PRES' in data.keys()):

                woa = db[vtype].track(
                        var=['mean', 'standard_deviation',
                            'number_of_observations'],
                        doy=int(data.attributes['datetime'].strftime('%j')),
                        depth=data['PRES'],
                        lat=data.attributes['LATITUDE'],
                        lon=data.attributes['LONGITUDE'])

    flag = np.zeros(data[v].shape, dtype='i1')
    features = {}

    try:
        woa_bias = data[v] - woa['mean']
        woa_normbias = woa_bias / woa['standard_deviation']

        ind = np.nonzero((woa['number_of_observations'] >= min_samples) &
                (np.absolute(woa_normbias) <= cfg['sigma_threshold']))
        flag[ind] = 1   # cfg['flag_good']
        ind = np.nonzero((woa['number_of_observations'] >= min_samples) &
                (np.absolute(woa_normbias) > cfg['sigma_threshold']))
        flag[ind] = 3   # cfg['flag_bad']

        # Flag as 9 any masked input value
        flag[ma.getmaskarray(data[v])] = 9

        features = {'woa_bias': woa_bias, 'woa_normbias': woa_normbias,
                'woa_std': woa['standard_deviation'],
                'woa_nsamples': woa['number_of_observations'],
                'woa_mean': woa['mean']}

    finally:
        # self.logger.warnning("%s - WOA is not available at this site" %
        # self.name)
        return flag, features


class WOA_NormBias(QCCheckVar):
    """Compares measurements with WOA climatology

    Notes
    -----
    * Although using standard error is a good idea, the default is to not use
      standard error to estimate the bias to follow the traaditional approach.
      This can have a signifcant impact in the deep oceans and regions lacking
      extensive sampling.
    """

    flag_bad = 3
    use_standard_error = False

    def __init__(self, data, varname, cfg=None, autoflag=True):
        try:
            self.use_standard_error = cfg["use_standard_error"]
        except (KeyError, TypeError):
            module_logger.debug("use_standard_error undefined. Using default value")
        super().__init__(data, varname, cfg, autoflag)


    def set_features(self):
        try:
            doy = int(self.data.attrs['date'].strftime('%j'))
        except:
            doy = int(self.data.attrs['datetime'].strftime('%j'))

        if ('LATITUDE' in self.data.attrs.keys()) and \
                ('LONGITUDE' in self.data.attrs.keys()):
                    mode = 'profile'
                    kwargs = {
                            'lat': self.data.attrs['LATITUDE'],
                            'lon': self.data.attrs['LONGITUDE']}

        if ('LATITUDE' in self.data.keys()) and \
                ('LONGITUDE' in self.data.keys()):
                    mode = 'track'
                    dLmax = max(
                            self.data['LATITUDE'].max() - self.data['LATITUDE'].min(),
                            self.data['LONGITUDE'].max() - self.data['LONGITUDE'].min())
                    # Only use each measurement coordinate if it is spread.
                    if dLmax >= 0.01:
                        kwargs = {
                            'lat': self.data['LATITUDE'],
                            'lon': self.data['LONGITUDE']}

        if ('DEPTH' in self.data.keys()):
            depth = self.data['DEPTH']
        elif ('PRES' in self.data.keys()):
            depth = self.data['PRES']

        db = WOA()
        if self.varname[-1] == '2':
            vtype = self.varname[:-1]
        else:
            vtype = self.varname

        woa_vars = ['mean', 'standard_deviation', 'standard_error',
                    'number_of_observations']

        idx = ~ma.getmaskarray(depth) & np.array(depth >= 0)
        if idx.any():
            if mode == 'track':
                woa = db[vtype].track(
                        var=woa_vars,
                        doy=doy,
                        depth=depth[idx],
                        **kwargs)
            else:
                woa = db[vtype].extract(
                        var=woa_vars,
                        doy=doy,
                        depth=depth[idx],
                        **kwargs)
        else:
            woa = {v: ma.masked_all(1) for v in woa_vars}

        if idx.all() is not True:
            for v in woa.keys():
                tmp = ma.masked_all(depth.shape, dtype=woa[v].dtype)
                tmp[idx] = woa[v]
                woa[v] = tmp

        self.features = {
                'woa_mean': woa['mean'],
                'woa_std': woa['standard_deviation'],
                'woa_nsamples': woa['number_of_observations'],
                'woa_se': woa['standard_error']}

        self.features['woa_bias'] = self.data[self.varname] - \
                self.features['woa_mean']

        # if use_standard_error = True, the comparison with the climatology
        #   considers the standard error, i.e. the bias will be only the
        #   ammount above the standard error range.
        if self.use_standard_error is True:
            standard_error = self.features['woa_std'] / \
                    self.features['woa_nsamples'] ** 0.5
            idx = np.absolute(self.features['woa_bias']) <= \
                    standard_error
            self.features['woa_bias'][idx] = 0
            idx = np.absolute(self.features['woa_bias']) > standard_error
            self.features['woa_bias'][idx] -= \
                    np.sign(self.features['woa_bias'][idx]) * \
                    standard_error[idx]

        self.features['woa_normbias'] = self.features['woa_bias'] / \
                self.features['woa_std']

    def test(self):

        # 3 is the possible minimum to estimate the std, but I shold use higher.
        try:
            min_samples = self.cfg['min_samples']
        except KeyError:
            min_samples = 3

        self.flags = {}

        threshold = self.cfg['threshold']
        assert (np.size(threshold) == 1) and \
                (threshold is not None)

        flag = np.zeros(self.data[self.varname].shape, dtype='i1')

        normbias_abs = np.absolute(self.features['woa_normbias'])
        ind = np.nonzero((self.features['woa_nsamples'] >= min_samples) &
                (normbias_abs <= threshold))
        flag[ind] = self.flag_good
        ind = np.nonzero((self.features['woa_nsamples'] >= min_samples) &
                (normbias_abs > threshold))
        flag[ind] = self.flag_bad

        # Flag as 9 any masked input value
        flag[ma.getmaskarray(self.data[self.varname])] = 9

        self.flags['woa_normbias'] = flag
