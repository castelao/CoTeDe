# -*- coding: utf-8 -*-

"""

    Based on Argo's density inversion test. Test 14 @ Argo QC 2.9.1
"""

import logging

import numpy as np
from numpy import ma

from .qctests import QCCheck

module_logger = logging.getLogger(__name__)

try:
    import gsw

    nogsw = False
except ImportError:
    module_logger.info("Missing package GSW, used to estimate density when needed.")
    nogsw = True


def densitystep(S, T, P, auto_rotate=False):
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

    if nogsw:
        print("Package gsw is required and is not available.")

    rho0 = gsw.pot_rho_t_exact(S, T, P, 0)
    ds = ma.concatenate([ma.masked_all(1), np.sign(np.diff(P)) * np.diff(rho0)])
    return ma.fix_invalid(ds)


class DensityInversion(QCCheck):
    def __init__(self, data, cfg, autoflag=True):
        assert "TEMP" in data.keys(), "Missing TEMP"
        assert "PSAL" in data.keys(), "Missing PSAL"
        assert "PRES" in data.keys(), "Missing PRES"

        self.data = data
        self.cfg = cfg

        self.set_features()
        if autoflag:
            self.test()

    def set_features(self):
        self.features = {
            "densitystep": densitystep(
                self.data["PSAL"], self.data["TEMP"], self.data["PRES"]
            )
        }

    def test(self):
        self.flags = {}

        assert (
            (np.size(self.cfg["threshold"]) == 1)
            and (self.cfg["threshold"] is not None)
            and (np.isfinite(self.cfg["threshold"]))
        )

        flag = np.zeros(self.data["TEMP"].shape, dtype="i1")
        threshold = self.cfg["threshold"]
        feature = self.features["densitystep"]
        flag[np.nonzero(feature < threshold)] = self.flag_bad
        flag[np.nonzero(feature >= threshold)] = self.flag_good
        mask = np.any(
            [ma.getmaskarray(self.data[v]) for v in ["PRES", "TEMP", "PSAL"]], axis=0
        )
        flag[mask] = 9
        self.flags["density_inversion"] = flag
