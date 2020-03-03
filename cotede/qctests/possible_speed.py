# -*- coding: utf-8 -*-

import numpy as np
from numpy import ma
from numpy import radians

AVG_EARTH_RADIUS = 6371000  # in m


def haversine(lat_a, lon_a, lat_b, lon_b):
    """

        Copied from MAUD.
    """

    lat_a, lon_a, lat_b, lon_b = map(radians, [lat_a, lon_a, lat_b, lon_b])

    dlat = lat_a - lat_b
    dlon = lon_a - lon_b
    d = np.sin(dlat / 2) ** 2 + np.cos(lat_a) * np.cos(lat_b) * np.sin(dlon / 2) ** 2
    h = 2 * AVG_EARTH_RADIUS * np.arcsin(np.sqrt(d))

    return h


def speed(data):
    """
    """
    assert "timeS" in data.keys(), "Missing timeS in input data"
    assert "LATITUDE" in data.keys(), "Missing LATITUDE in input data"
    assert "LONGITUDE" in data.keys(), "Missing LONGITUDE in input data"

    dL = haversine(
        data["LATITUDE"][:-1],
        data["LONGITUDE"][:-1],
        data["LATITUDE"][1:],
        data["LONGITUDE"][1:],
    )
    dt = ma.diff(data["timeS"])

    speed = ma.append(ma.masked_array([0], [True]), dL / dt)

    return speed


def possible_speed(data, cfg):
    """

        Consider 4 if smooth is higher, 3 if smooth smaller, 1 if raw smaller
    """
    s = speed(data)

    flag = np.zeros(s.shape, dtype="i1")

    flag[s <= cfg["threshold"]] = cfg["flag_good"]
    flag[s > cfg["threshold"]] = cfg["flag_bad"]

    # Flag as 9 any masked input value
    # for v in ['LATITUDE', 'LONGITUDE']:
    #    flag[ma.getmaskarray(data[v])] = 9
    # I'm not sure if it's a good idea. I should flag as 9 if the variable
    #   being tested is invalid. For example, if I have a good temperature,
    #   but no valid location, the possible_speed test should return 0, i.e.
    #   no Q.C. evaluated.

    return flag, s
