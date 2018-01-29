# -*- coding: utf-8 -*-

"""
"""

from datetime import timedelta

import numpy as np
from numpy import ma

from oceansdb import CARS


class CARS_NormBias(object):
    def __init__(self, data, varname, cfg):
        self.data = data
        self.varname = varname
        self.cfg = cfg

        # Default is to do not use standard error to estimate the bias,
        #   because that is the traditional approach.
        if 'use_standard_error' not in self.cfg:
            self.cfg['use_standard_error'] = False

        self.set_features()
        try:
            self.test()
        except:
            pass

    def keys(self):
        return self.features.keys() + \
                ["flag_%s" % f for f in self.flags.keys()]

    def set_features(self):

        if ('LATITUDE' in self.data.attributes.keys()) and \
                ('LONGITUDE' in self.data.attributes.keys()):
                    kwargs = {
                            'lat': self.data.attributes['LATITUDE'],
                            'lon': self.data.attributes['LONGITUDE']}

        if ('LATITUDE' in self.data.keys()) and \
                ('LONGITUDE' in self.data.keys()):
                    dLmax = max(
                            data['LATITUDE'].max()-data['LATITUDE'].min(),
                            data['LONGITUDE'].max()-data['LONGITUDE'].min())
                    # Only use each measurement coordinate if it is spread.
                    if dLmax >= 0.01:
                        kwargs = {
                            'lat': self.data['LATITUDE'],
                            'lon': self.data['LONGITUDE'],
                            'alongtrack_axis': ['lat', 'lon']}

        if ('DEPTH' in self.data.keys()):
            depth = self.data['DEPTH']
        elif ('PRES' in self.data.keys()):
            depth = self.data['PRES']

        try:
            doy = int(self.data.attributes['date'].strftime('%j'))
        except:
            doy = int(self.data.attributes['datetime'].strftime('%j'))

        db = CARS()
        if self.varname[-1] == '2':
            vtype = self.varname[:-1]
        else:
            vtype = self.varname

        cars = db[vtype].extract(
                var=['mn', 'std_dev'],
                doy=doy,
                depth=depth,
                **kwargs)

        self.features = {
                'cars_mean': cars['mn'],
                'cars_std': cars['std_dev']}

        self.features['cars_bias'] = self.data[self.varname] - \
                self.features['cars_mean']

        # if use_standard_error = True, the comparison with the climatology
        #   considers the standard error, i.e. the bias will be only the
        #   ammount above the standard error range.
        assert not self.cfg['use_standard_error']
        if self.cfg['use_standard_error'] is True:
            standard_error = self.features['cars_std'] / \
                    self.features['cars_nsamples'] ** 0.5
            idx = np.absolute(self.features['cars_bias']) <= \
                    standard_error
            self.features['cars_bias'][idx] = 0
            idx = np.absolute(self.features['cars_bias']) > standard_error
            self.features['cars_bias'][idx] -= \
                    np.sign(self.features['cars_bias'][idx]) * \
                    standard_error[idx]

        self.features['cars_normbias'] = self.features['cars_bias'] / \
                self.features['cars_std']

    def test(self):

        # 3 is the possible minimum to estimate the std, but I shold use higher.
        try:
            min_samples = self.cfg['min_samples']
        except:
            min_samples = 3

        self.flags = {}

        try:
            flag_good = self.cfg['flag_good']
        except:
            flag_good = 1
        try:
            flag_bad = self.cfg['flag_bad']
        except:
            flag_bad = 3

        threshold = self.cfg['threshold']
        assert (np.size(threshold) == 1) and \
                (threshold is not None)

        flag = np.zeros(self.data[self.varname].shape, dtype='i1')

        normbias_abs = np.absolute(self.features['cars_normbias'])
        ind = np.nonzero(normbias_abs <= threshold)
        flag[ind] = flag_good
        ind = np.nonzero(normbias_abs > threshold)
        flag[ind] = flag_bad

        # Flag as 9 any masked input value
        flag[ma.getmaskarray(self.data[self.varname])] = 9

        self.flags['cars_normbias'] = flag
