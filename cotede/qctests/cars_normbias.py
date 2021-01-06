# -*- coding: utf-8 -*-

"""
"""

from datetime import timedelta
import logging

import numpy as np
from numpy import ma
from oceansdb import CARS

from . import QCCheckVar
from ..utils import extract_coordinates, extract_time, day_of_year, extract_depth


module_logger = logging.getLogger(__name__)


def cars_normbias(data, varname, attrs=None, use_standard_error=False):
    """

    Notes
    -----
    - Include arguments to overwrite target variable (timename=None, latname=None, lonname=None)

    """
    try:
        doy = day_of_year(extract_time(data, attrs))
    except LookupError as err:
        module_logger.error("Missing time")
        raise

    try:
        # Note that QCCheck fallback to self.data.attrs if attrs not given
        lat, lon = extract_coordinates(data, attrs)
    except LookupError:
        module_logger.error("Missing geolocation (lat/lon)")
        raise

    kwargs = {"lat": lat, "lon": lon}

    if (np.size(lat) > 1) | (np.size(lon) > 1):
        dLmax = max(np.max(lat) - np.min(lat), np.max(lon) - np.min(lon))
        if dLmax >= 0.01:
            mode = "track"
            # kwargs["alongtrack_axis"] = ['lat', 'lon']
        else:
            mode = "profile"
            kwargs = {
                "lat": np.mean(lat),
                "lon": np.mean(lon),
            }
            module_logger.warning(
                "Multiple lat/lon positions but too close to each other so it will be considered a single position for the WOA comparison. lat: {}, lon: {}".format(
                    kwargs["lat"], kwargs["lon"]
                )
            )
    else:
        mode = "profile"

    depth = extract_depth(data)

    db = CARS()
    # This must go away. This was a trick to handle Seabird CTDs, but
    # now that seabird is a different package it should be handled there.
    if isinstance(varname, str) and (varname[-1] == "2"):
        vtype = varname[:-1]
    else:
        vtype = varname

    cars_vars = [
        "mean",
        # "standard_deviation",
        "std_dev",
        # "number_of_observations",
    ]

    # Eventually the case of some invalid depth levels will be handled by
    # OceansDB and the following steps will be simplified.
    valid_depth = depth
    if np.size(depth) > 0:
        idx = ~ma.getmaskarray(depth) & (np.array(depth) >= 0) & np.isfinite(depth)
        if not idx.any():
            module_logger.error(
                "Invalid depth(s) for CARS comparison: {}".format(depth)
            )
            raise IndexError
        elif not idx.all():
            valid_depth = depth[idx]
    if mode == "track":
        cars = db[vtype].track(var=cars_vars, doy=doy, depth=valid_depth, **kwargs)
    else:
        cars = db[vtype].extract(var=cars_vars, doy=doy, depth=valid_depth, **kwargs)

    if not np.all(depth == valid_depth):
        for v in cars.keys():
            tmp = ma.masked_all(depth.shape, dtype=cars[v].dtype)
            tmp[idx] = cars[v]
            cars[v] = tmp

    features = {
        "cars_mean": cars["mean"],
        "cars_std": cars["std_dev"],
        # "cars_nsamples": cars["number_of_observations"],
    }

    features["cars_bias"] = data[varname] - features["cars_mean"]

    for v in features:
        idx = ma.getmaskarray(features[v])
        if idx.any():
            if v == "cars_nsamples":
                missing_value = -1
            else:
                missing_value = np.nan
            features[v][idx] = missing_value
        features[v] = np.array(features[v])

    # if use_standard_error = True, the comparison with the climatology
    #   considers the standard error, i.e. the bias will be only the
    #   ammount above the standard error range.
    if use_standard_error is True:
        standard_error = features["cars_std"]
        idx = features["cars_nsamples"] > 0
        standard_error[~idx] = np.nan
        standard_error[idx] /= features["cars_nsamples"][idx] ** 0.5

        idx = np.absolute(features["cars_bias"]) <= standard_error
        features["cars_bias"][idx] = 0
        idx = np.absolute(features["cars_bias"]) > standard_error
        features["cars_bias"][idx] -= (
            np.sign(features["cars_bias"][idx]) * standard_error[idx]
        )

    features["cars_normbias"] = features["cars_bias"] / features["cars_std"]

    return features


class CARS_NormBias(QCCheckVar):
    """Compares measuremnts with CARS climatology

    Notes
    -----
    * Although using standard error is a good idea, the default is to not use
      standard error to estimate the bias to follow the traaditional approach.
      This can have a signifcant impact in the deep oceans and regions lacking
      extensive sampling.
    """

    flag_bad = 3
    use_standard_error = False
    # 3 is the possible minimum to estimate the std, but I shold use higher.
    min_samples = 3

    def __init__(self, data, varname, cfg=None, autoflag=True):
        try:
            self.use_standard_error = cfg["use_standard_error"]
        except (KeyError, TypeError):
            module_logger.debug("use_standard_error undefined. Using default value")
        try:
            self.min_samples = cfg["min_samples"]
        except (KeyError, TypeError):
            module_logger.debug("min_samples undefined. Using default value")

        super().__init__(data, varname, cfg, autoflag)

    def set_features(self):
        try:
            self.features = cars_normbias(self.data, self.varname, self.attrs)
        except LookupError:
            self.features = {}

    def test(self):
        self.flags = {}

        threshold = self.cfg["threshold"]
        assert (np.size(threshold) == 1) and (threshold is not None)

        flag = np.zeros(self.data[self.varname].shape, dtype="i1")

        if "cars_normbias" not in self.features:
            self.flags["cars_normbias"] = flag
            return

        normbias_abs = np.absolute(self.features["cars_normbias"])
        ind = np.nonzero(normbias_abs <= threshold)
        flag[ind] = self.flag_good
        ind = np.nonzero(normbias_abs > threshold)
        flag[ind] = self.flag_bad

        # Flag as 9 any masked input value
        flag[ma.getmaskarray(self.data[self.varname])] = 9

        self.flags["cars_normbias"] = flag
