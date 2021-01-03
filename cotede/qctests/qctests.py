# -*- coding: utf-8 -*-

""" The tests itself to QC the data
"""

import logging

import numpy as np
from numpy import ma

module_logger = logging.getLogger(__name__)


# FIXME, tests to adjust on public version
def frozen_profile():
    pass


def grey_list():
    pass


def valid_speed():
    pass


def gross_sensor_drift():
    pass


def platform_identification():
    pass


class QCCheck(object):
    """Basic template for a QC check
    """

    flag_good = 1
    flag_bad = 4

    def __init__(self, data, *, cfg=None, autoflag=True, attrs=None):
        self.data = data
        if (cfg is not None):
            self.cfg = cfg
        elif not hasattr(self, 'cfg'):
            self.cfg = {}

        if attrs is not None:
            self._attrs = attrs

        self.set_flags()
        self.set_features()
        if autoflag:
            self.test()

    def __getitem__(self, key):
        return self.data[key]

    @property
    def attrs(self):
        if hasattr(self, '_attrs'):
            return self._attrs
        return self.data.attrs

    def set_features(self):
        self.features = {}

    def set_flags(self):
        try:
            self.flag_good = self.cfg["flag_good"]
        except (KeyError, TypeError):
            module_logger.debug("flag_good undefined. Using default value")

        try:
            self.flag_bad = self.cfg["flag_bad"]
        except (KeyError, TypeError):
            module_logger.debug("flag_bad undefined. Using default value")

    def keys(self):
        return self.features.keys() + ["flag_%s" % f for f in self.flags.keys()]

    def test(self):
        """Actual test evaluation procedure: Expected from derived objects
        """
        raise NotImplementedError


class QCCheckVar(QCCheck):
    """Template for a QC check of a specific variable
    """

    def __init__(self, data, varname, cfg=None, autoflag=True):
        self.varname = varname
        super().__init__(data=data, cfg=cfg, autoflag=autoflag)
