# -*- coding: utf-8 -*-

"""

    Based on ARGO's density inversion test. Test 14 @ ARGO QC 2.9.1
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
        assert S.ndim == 1, "Not able to densitystep an array ndim > 1"
        ds = ma.concatenate([ma.masked_all(1),
                np.sign(np.diff(P))*np.diff(rho0)])
        return ma.fix_invalid(ds)

    except ImportError:
        print("Package gsw is required and is not available.")


def density_inversion(data, cfg, saveaux=False):
    """

        Must decide where to set the flags.
    """
    assert ('TEMP' in data.keys()), \
            "Missing TEMP"
    assert ('PSAL' in data.keys()), \
            "Missing PSAL"
    assert ('PRES' in data.keys()), \
            "Missing PRES"

    ds = densitystep(data['TEMP'], data['PSAL'],
            data['PRES'])

    if ds is None:
        # FIXME:
        print("Improve error handling. Package gsw is not available")
        return

    flag = np.zeros(ds.shape, dtype='i1')

    flag[np.nonzero(ds >= cfg['threshold'])] = cfg['flag_good']
    flag[np.nonzero(ds < cfg['threshold'])] = cfg['flag_bad']

    # Flag as 9 any masked input value
    #for v in ['TEMP', 'PSAL', 'PRES']:
    #    flag[ma.getmaskarray(data[v])] = 9

    if saveaux:
        return flag, ds
    else:
        return flag
