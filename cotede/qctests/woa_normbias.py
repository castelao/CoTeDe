# -*- coding: utf-8 -*-

"""

"""

import numpy as np
from numpy import ma
from cotede.utils import woa_profile


def woa_normbias(data, v, cfg):

    if ('latitude' not in data.keys()) and \
            ('longitude' not in data.keys()):
                woa = woa_profile(v,
                        data.self.attributes['datetime'],
                        data.attributes['latitude'],
                        data.attributes['longitude'],
                        data['PRES'],
                        cfg)
    else:
        woa = None

    if woa is None:
        # self.logger.warn("%s - WOA is not available at this site" %
        # self.name)
        return None, None

    woa_bias = ma.absolute(data[v] - woa['woa_an'])
    woa_normbias = woa_bias/woa['woa_sd']


    flag = np.zeros(data[v].shape, dtype='i1')

    ind = np.nonzero(woa_normbias <= cfg['woa_comparison']['sigma_threshold'])
    flag[ind] = 1   # cfg['flag_good']
    ind = np.nonzero(woa_normbias > cfg['woa_comparison']['sigma_threshold'])
    flag[ind] = 3   # cfg['flag_bad']

    # Flag as 9 any masked input value
    flags[ma.getmaskarray(data[v])] = 9


    return flag, woa_normbias
