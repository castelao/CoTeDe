# -*- coding: utf-8 -*-

""" The tests itself to QC the data
"""

import logging

import numpy as np
from numpy import ma


module_logger = logging.getLogger(__name__)


def step(x):
    y = ma.masked_all(x.shape, dtype=x.dtype)
    y[1:] = ma.diff(x)
    return y


# FIXME, tests to adjust on public version
def valid_datetime():
    pass


def frozen_profile():
    pass


def valid_geolocation():
    pass


def valid_position():
    pass

def deepest_pressure():
    pass

def regional_range():
    pass


def grey_list():
    pass


def gradient_depthconditional():
    pass


def spike_depthconditional():
    pass


def digit_roll_over():
    pass


def valid_speed():
    pass


def gross_sensor_drift():
    pass


def pressure_increasing():
    pass


def stuck_value():
    pass


def platform_identification():
    pass


def pstep():
    pass


def constant_value():
    pass


class QCCheck(object):
    """Basic template for a QC check
    """

    flag_good = 1
    flag_bad = 4

    def __init__(self, data, cfg=None, autoflag=True):
        self.data = data
        self.cfg = cfg

        self.set_flags()
        self.set_features()
        if autoflag:
            self.test()

    def __getitem__(self, key):
        return self.data[key]

    @property
    def attrs(self):
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


class QCCheckVar(QCCheck):
    """Template for a QC check of a specific variable
    """

    def __init__(self, data, varname, cfg=None, autoflag=True):
        self.varname = varname
        super().__init__(data, cfg, autoflag)
