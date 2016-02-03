# -*- coding: utf-8 -*-

""" The tests itself to QC the data
"""

import numpy as np
from numpy import ma

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
