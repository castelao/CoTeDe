# -*- coding: utf-8 -*-

"""

    Based on ARGO tests definition. Test 14 @ ARGO QC 2.9.1
"""

import numpy as np
from numpy import ma

def densitystep(S, T, P):
    """
    """
    assert S.shape == T.shape
    assert S.shape == P.shape
    try:
        import gsw
        rho0 = gsw.pot_rho_t_exact(S, T, P, 0)
        ds = ma.append(ma.masked_all(1),
                np.sign(np.diff(P))*np.diff(rho0))
        return ds

    except ImportError:
        print("Package gsw is required and is not available.")


def density_inverison(data, cfg):
    """

    """
    assert ('temperature' in data.attributes), \
            "Missing temperature in attributes"
    assert ('salinity' in data.attributes), \
            "Missing salinity in attributes"
    assert ('pressure' in data.attributes), \
            "Missing pressure in attributes"

    ds = densitystep(data['temperature'], data['salinity'],
            data['pressure'])

    flag = np.zeros(ds.shape, dtype='i1')
    flag[ds >= -0.03] = 1
    flag[ds < -0.03] = 4

    return flag
