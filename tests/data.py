# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

from datetime import datetime
import numpy as np
from numpy import ma


class DummyData(object):
    def __init__(self):
        self.attributes = {
                'datetime': datetime(2016,6,4),
                'LATITUDE': 15, 'LONGITUDE': -38}
        self.data = {
                'PRES': ma.masked_array([0.0, 100, 200, 5000]),
                'TEMP': ma.masked_array([25.16, 19.73, 16.80, 2.12]),
                'PSAL': ma.masked_array([32.00, 34.74, 34.66, 35.03])}

    def __getitem__(self, key):
        return self.data[key]

    def keys(self):
        return self.data.keys()
