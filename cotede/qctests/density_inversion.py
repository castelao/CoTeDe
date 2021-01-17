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

    GSW_AVAILABLE = True
except ImportError:
    module_logger.debug("Missing package GSW, used to estimate density when needed.")
    GSW_AVAILABLE = False


def densitystep(SA, t, p, auto_rotate=False):
    """Estimates the potential density step of successive mesurements

       Expects the data to be recorded along the time, i.e. first measurement
         was recorded first. This makes difference since the first measurement
         has no reference to define the delta change.
       This is relevant for the type of instrument. For instance: XBTs are
         always measured surface to bottom, CTDs are expected the same, but
         Spray underwater gliders measure bottom to surface.
    """
    assert np.shape(t) == np.shape(p)
    assert np.shape(t) == np.shape(SA)
    assert np.ndim(t) == 1, "Not ready to densitystep an array ndim > 1"

    rho0 = gsw.pot_rho_t_exact(SA, t, p, 0)
    y = np.nan * np.atleast_1d(t)
    y[1:] = np.sign(np.diff(p)) * np.diff(rho0)

    if isinstance(y, ma.MaskedArray):
        y[y.mask] = np.nan
        y = y.data

    return y


class DensityInversion(QCCheck):
    def __init__(self, data, cfg, autoflag=True):
        assert "TEMP" in data.keys(), "Missing TEMP"
        assert "PSAL" in data.keys(), "Missing PSAL"
        assert "PRES" in data.keys(), "Missing PRES"

        super().__init__(data=data, cfg=cfg, autoflag=autoflag)

    def set_features(self):
        if not GSW_AVAILABLE:
            module_logger.warning("DensityInversion requires gsw!")
            self.features = {}
            return

        self.features = {
            "densitystep": densitystep(
                self.data["PSAL"], self.data["TEMP"], self.data["PRES"]
            )
        }

    def test(self):
        self.flags = {}
        try:
            threshold = self.cfg["threshold"]
        except KeyError:
            module_logger.warning(
                "Deprecated cfg format. It should contain a threshold item."
            )
            threshold = self.cfg

        assert np.size(self.cfg["threshold"]) == 1
        assert self.cfg["threshold"] is not None
        assert np.isfinite(self.cfg["threshold"])

        flag = np.zeros(np.shape(self.data["TEMP"]), dtype="i1")

        if ("densitystep" not in self.features) and not GSW_AVAILABLE:
            module_logger.warning("Couldn't estimate density without GSW")
            self.flags["density_inversion"] = flag
            return

        feature = self.features["densitystep"]
        # Note the comparison is opposite of the usual (good if >=)
        flag[feature < threshold] = self.flag_bad
        flag[feature >= threshold] = self.flag_good
        self.flags["density_inversion"] = flag
