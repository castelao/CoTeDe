# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

""" The tests itself to QC the data
"""

import logging

import numpy as np
from numpy import ma

module_logger = logging.getLogger(__name__)


class QCCheck(object):
    """Basic template for a QC check
    """

    flag_good = 1
    flag_bad = 4

    def __init__(self, data, *, cfg=None, autoflag=True, attrs=None, cars_db=None, woa_db=None, etopo_dbs=None):
        self.data = data
        self._cars_db = cars_db
        self._woa_db = woa_db
        self._etopo_dbs = etopo_dbs
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

    def __init__(self, data, varname, cfg=None, autoflag=True, attrs=None, cars_db=None, woa_db=None, etopo_dbs=None):
        self.varname = varname
        super().__init__(data=data, cfg=cfg, autoflag=autoflag, attrs=attrs, cars_db=cars_db, woa_db=woa_db, etopo_dbs=etopo_dbs)
