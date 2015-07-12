# -*- coding: utf-8 -*-

"""

"""

from datetime import timedelta

import numpy as np
from numpy import ma
from cotede.utils import woa_profile, woa_track_from_file


def woa_normbias(data, v, cfg):

    if ('latitude' in data.keys()) and \
            ('longitude' in data.keys()):
                print("Temporary solution!! This is wrong!!")
                #if 'datetime' not in data.keys():
                #    d0 = data.attributes['datetime']
                #    data.data['datetime'] = \
                #            [d0 + timedelta(seconds=t) for t in data['timeS']]
                woa = woa_track_from_file(
                        [data.attributes['datetime']]*len(data['latitude']),
                        data['latitude'],
                        data['longitude'],
                        cfg['file'],
                        varnames=cfg['vars'])
    else:
                woa = woa_profile(v,
                        data.attributes['datetime'],
                        data.attributes['latitude'],
                        data.attributes['longitude'],
                        data['PRES'],
                        cfg)

    if woa is None:
        # self.logger.warn("%s - WOA is not available at this site" %
        # self.name)
        return None, None

    woa_bias = ma.absolute(data[v] - woa['woa_an'])
    woa_normbias = woa_bias/woa['woa_sd']


    flag = np.zeros(data[v].shape, dtype='i1')

    ind = np.nonzero(woa_normbias <= cfg['sigma_threshold'])
    flag[ind] = 1   # cfg['flag_good']
    ind = np.nonzero(woa_normbias > cfg['sigma_threshold'])
    flag[ind] = 3   # cfg['flag_bad']

    # Flag as 9 any masked input value
    flag[ma.getmaskarray(data[v])] = 9


    return flag, woa_normbias
