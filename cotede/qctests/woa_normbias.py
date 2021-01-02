# -*- coding: utf-8 -*-

"""


    Create a test to check if cfg['vars'] does exist in the climatology file,
      to avoid error like have t_mn in one and t_an in the other.

    An idea to improve the climatology test. Gridpoints estimated from few
      measurements should be less trustable. Here I'm using a threshold of at
      least 3 samples to be considered. Deep ocean is in general quite
      stable, so few measurements should be sufficient. One possibility is to
      estimate the standard error, which depends on the ammount of samples and
      estimated standard deviation. This would be the 'uncertainty on the
      estimated average climatology. Any measurement in that range would be
      considered statistically identical to the climatology. Above that
      difference, it would be normalized by the standard deviation. Therefore,
      stable areas would be less tolerant to variability, even with few samples.
"""

from datetime import timedelta
import logging

import numpy as np
from numpy import ma
from oceansdb import WOA

from .qctests import QCCheckVar
from ..utils import extract_coordinates, extract_time, day_of_year, extract_depth

module_logger = logging.getLogger(__name__)


def woa_normbias(data, varname, attrs=None, use_standard_error=False):
    """

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
            module_logger.warning("Multiple lat/lon positions but too close to each other so it will be considered a single position for the WOA comparison. lat: {}, lon: {}".format(kwargs["lat"], kwargs["lon"]))
    else:
        mode = "profile"

    depth = extract_depth(data)

    db = WOA()
    # This must go away. This was a trick to handle Seabird CTDs, but
    # now that seabird is a different package it should be handled there.
    if isinstance(varname, str) and (varname[-1] == "2"):
        vtype = varname[:-1]
    else:
        vtype = varname

    woa_vars = [
        "mean",
        "standard_deviation",
        "standard_error",
        "number_of_observations",
    ]

    # Eventually the case of some invalid depth levels will be handled by
    # OceansDB and the following steps will be simplified.
    valid_depth = depth
    if (np.size(depth) > 0):
        idx = ~ma.getmaskarray(depth) & (np.array(depth) >= 0) & np.isfinite(depth)
        if not idx.any():
            module_logger.error("Invalid depth(s) for WOA comparison: {}".format(depth))
            raise IndexError
        elif not idx.all():
            valid_depth = depth[idx]
    if mode == "track":
        woa = db[vtype].track(var=woa_vars, doy=doy, depth=valid_depth, **kwargs)
    else:
        woa = db[vtype].extract(var=woa_vars, doy=doy, depth=valid_depth, **kwargs)

    if not np.all(depth == valid_depth):
        for v in woa.keys():
            tmp = ma.masked_all(depth.shape, dtype=woa[v].dtype)
            tmp[idx] = woa[v]
            woa[v] = tmp

    features = {
        "woa_mean": woa["mean"],
        "woa_std": woa["standard_deviation"],
        "woa_nsamples": woa["number_of_observations"],
        "woa_se": woa["standard_error"],
    }

    features["woa_bias"] = data[varname] - features["woa_mean"]

    for v in features:
        idx = ma.getmaskarray(features[v])
        if idx.any():
            if v == "woa_nsamples":
                missing_value = -1
            else:
                missing_value = np.nan
            features[v][idx] = missing_value
        features[v] = np.array(features[v])

    # if use_standard_error = True, the comparison with the climatology
    #   considers the standard error, i.e. the bias will be only the
    #   ammount above the standard error range.
    if use_standard_error is True:
        standard_error = features["woa_std"]
        idx = features["woa_nsamples"] > 0
        standard_error[~idx] = np.nan
        standard_error[idx] /= features["woa_nsamples"][idx] ** 0.5

        idx = np.absolute(features["woa_bias"]) <= standard_error
        features["woa_bias"][idx] = 0
        idx = np.absolute(features["woa_bias"]) > standard_error
        features["woa_bias"][idx] -= (
            np.sign(features["woa_bias"][idx]) * standard_error[idx]
        )

    features["woa_normbias"] = features["woa_bias"] / features["woa_std"]

    return features


class WOA_NormBias(QCCheckVar):
    """Compares measurements with WOA climatology

    Notes
    -----
    * Although using standard error is a good idea, the default is to not use
      standard error to estimate the bias to follow the traaditional approach.
      This can have a signifcant impact in the deep oceans and regions lacking
      extensive sampling.

        FIXME: Move this procedure into a class to conform with the new system
          and include a limit in minimum ammount of samples to trust it. For
          example, consider as masked all climatologic values estimated from
          less than 5 samples.
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
            self.features = woa_normbias(self.data, self.varname, self.attrs)
        except LookupError:
            self.features = {}

    def test(self):
        self.flags = {}

        threshold = self.cfg["threshold"]
        assert (np.size(threshold) == 1) and (threshold is not None)

        flag = np.zeros(self.data[self.varname].shape, dtype="i1")

        normbias_abs = np.absolute(self.features["woa_normbias"])
        ind = np.nonzero(
            (self.features["woa_nsamples"] >= self.min_samples)
            & np.array(normbias_abs <= threshold)
        )
        flag[ind] = self.flag_good
        ind = np.nonzero(
            (self.features["woa_nsamples"] >= self.min_samples)
            & np.array(normbias_abs > threshold)
        )
        flag[ind] = self.flag_bad

        # Flag as 9 any masked input value
        x = self.data[self.varname]
        flag[ma.getmaskarray(x) | ~np.isfinite(np.array(x))] = 9

        self.flags["woa_normbias"] = flag
