# -*- coding: utf-8 -*-

""" The tests itself to QC the data
"""

import numpy as np
from numpy import ma

def step(x):
    y = ma.masked_all(x.shape, dtype=x.dtype)
    y[1:] = ma.diff(x)
    return y
