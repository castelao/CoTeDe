# -*- coding: utf-8 -*-

"""

    Based on Argo's density inversion test. Test 14 @ Argo QC 2.9.1
"""

import numpy as np
from numpy import ma
try:
    import gsw
except:
    pass


def densitystep(S, T, P):
    """Estimates the potential density step of successive mesurements

       Expects the data to be recorded along the time, i.e. first measurement
         was recorded first. This makes difference since the first measurement
         has no reference to define the delta change.
       This is relevant for the type of instrument. For instance: XBTs are
         always measured surface to bottom, CTDs are expected the same, but
         Spray underwater gliders measure bottom to surface.
    """
    assert T.shape == P.shape
    assert T.shape == S.shape
    assert T.ndim == 1, "Not ready to densitystep an array ndim > 1"

    try:
        import gsw
    except ImportError:
        print("Package gsw is required and is not available.")

    rho0 = gsw.pot_rho_t_exact(S, T, P, 0)
    ds = ma.concatenate([ma.masked_all(1),
        np.sign(np.diff(P))*np.diff(rho0)])
    return ma.fix_invalid(ds)


class DensityInversion(object):
    def __init__(self, data, cfg, autoflag=True):
        assert ('TEMP' in data.keys()), \
                "Missing TEMP"
        assert ('PSAL' in data.keys()), \
                "Missing PSAL"
        assert ('PRES' in data.keys()), \
                "Missing PRES"

        self.data = data
        self.cfg = cfg

        self.set_features()
        if autoflag:
            self.test()

    def keys(self):
        return self.features.keys() + \
            ["flag_%s" % f for f in self.flags.keys()]

    def set_features(self):
        self.features = {'densitystep': densitystep(self.data['PSAL'],
                                                    self.data['TEMP'],
                                                    self.data['PRES'])}

    def test(self):
        self.flags = {}
        try:
            threshold = self.cfg['threshold']
        except:
            print("Deprecated cfg format. It should contain a threshold item.")
            threshold = self.cfg

        try:
            flag_good = self.cfg['flag_good']
        except:
            flag_good = 1
        try:
            flag_bad = self.cfg['flag_bad']
        except:
            flag_bad = 4

        assert (np.size(threshold) == 1) and \
                (threshold is not None) and \
                (np.isfinite(threshold))

        mask = np.any([ma.getmaskarray(self.data[v]) for v in
            ['PRES', 'TEMP', 'PSAL']], axis=0)
        flag = np.zeros(mask.shape, dtype='i1')
        flag[np.nonzero(self.features['densitystep'] < threshold)] = flag_bad
        flag[np.nonzero(self.features['densitystep'] >= threshold)] = flag_good
        flag[mask] = 9
        self.flags['density_inversion'] = flag
