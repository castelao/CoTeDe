# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

from datetime import datetime
import numpy as np
from numpy import ma


class DummyData(object):
    def __init__(self):
        self.attrs = {
                'datetime': datetime(2016,6,4),
                'LATITUDE': 15, 'LONGITUDE': -38}
        self.data = {
                'PRES': ma.fix_invalid(
                    [2, 6, 10, 21, 44, 79, 100, 150,
                        200, 400, 410, 650, 1000, 2000, 5000]),
                'TEMP': ma.fix_invalid(
                    [25.32, 25.34, 25.34, 25.31, 24.99, 23.46, 21.85, 17.95,
                        15.39, 11.08, 6.93, 7.93, 5.71, 3.58, np.nan]),
                'PSAL': ma.fix_invalid(
                    [36.49, 36.51, 36.52, 36.53, 36.59, 36.76, 36.81, 36.39,
                        35.98, 35.30, 35.28, 34.93, 34.86, np.nan, np.nan])}

    def __getitem__(self, key):
        return self.data[key]

    def keys(self):
        return self.data.keys()

    @property
    def attributes(self):
        print('attributes will be removed. Use attrs instead!')
        return self.attrs
