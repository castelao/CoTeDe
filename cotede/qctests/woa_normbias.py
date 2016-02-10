# -*- coding: utf-8 -*-

"""


    Create a test to check if cfg['vars'] does exist in the climatology file,
      to avoid error like have t_mn in one and t_an in the other.
"""

from datetime import timedelta

import numpy as np
from numpy import ma

from pyWOA import WOA


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

    if ('LATITUDE' in data.keys()) and ('LONGITUDE' in data.keys()):
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
        db = WOA()
        if v not in db.keys():
            vtype = v[:-1]
        else:
            vtype = v

        woa = db[vtype].get_track(var=['mn', 'sd'],
                doy=d,
                depth=[0],
                lat=data['LATITUDE'],
                lon=data['LONGITUDE'])

    elif ('LATITUDE' in data.attributes.keys()) and \
            ('LONGITUDE' in data.attributes.keys()) and \
            ('PRES' in data.keys()):
                #woa = woa_profile(v,
                #        data.attributes['datetime'],
                #        data.attributes['LATITUDE'],
                #        data.attributes['LONGITUDE'],
                #        data['PRES'],
                #        cfg)
                db = WOA()
                if v not in db.keys():
                    vtype = v[:-1]
                else:
                    vtype = v

                woa = db[vtype].extract(var=['mn', 'sd', 'dd'],
                        doy=int(data.attributes['datetime'].strftime('%j')),
                        depth=data['PRES'],
                        lat=data.attributes['LATITUDE'],
                        lon=data.attributes['LONGITUDE'])

    if woa is None:
        # self.logger.warn("%s - WOA is not available at this site" %
        # self.name)
        flag = np.zeros(data[v].shape, dtype='i1')
        return flag, {}

    woa_bias = data[v] - woa['mn']
    woa_normbias = woa_bias/woa['sd']


    flag = np.zeros(data[v].shape, dtype='i1')

    ind = np.nonzero((woa['dd'] >= min_samples) &
            (np.absolute(woa_normbias) <= cfg['sigma_threshold']))
    flag[ind] = 1   # cfg['flag_good']
    ind = np.nonzero((woa['dd'] >= min_samples) &
            (np.absolute(woa_normbias) > cfg['sigma_threshold']))
    flag[ind] = 3   # cfg['flag_bad']

    # Flag as 9 any masked input value
    flag[ma.getmaskarray(data[v])] = 9

    features = {'woa_normbias': woa_normbias, 'woa_std': woa['sd'],
            'woa_nsamples': woa['dd']}

    return flag, features
