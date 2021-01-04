#!/usr/bin/env python

from .qctests import *
from .core import QCCheck, QCCheckVar
from .descentPrate import descentPrate
from .anomaly_detection import anomaly_detection
from .possible_speed import possible_speed
from .fuzzylogic import fuzzylogic
from .morello2014 import Morello2014, morello2014

from .bin_spike import Bin_Spike, bin_spike
from .cars_normbias import CARS_NormBias, cars_normbias
from .constant_cluster_size import ConstantClusterSize, constant_cluster_size
from .cum_rate_of_change import CumRateOfChange, cum_rate_of_change
from .deepest_pressure import DeepestPressure
from .density_inversion import DensityInversion, densitystep
from .digit_roll_over import DigitRollOver
from .global_range import GlobalRange
from .gradient import Gradient, gradient
from .gradient_depthconditional import GradientDepthConditional
from .location_at_sea import LocationAtSea, location_at_sea
from .monotonic_z import MonotonicZ
from .profile_envelop import ProfileEnvelop
from .regional_range import RegionalRange
from .rate_of_change import RateOfChange, rate_of_change
from .spike import Spike, spike
from .spike_depthconditional import SpikeDepthConditional
from .tukey53H import Tukey53H, tukey53H, tukey53H_norm
from .woa_normbias import WOA_NormBias, woa_normbias
from .stuck_value import StuckValue
from .valid_geolocation import ValidGeolocation

from .morello2014 import Morello2014, morello2014


QCTESTS = {
    "Bin_Spike": Bin_Spike,
    "CARS_NormBias": CARS_NormBias,
    "ConstantClusterSize": ConstantClusterSize,
    "CumRateOfChange": CumRateOfChange,
    "DeepestPressure": DeepestPressure,
    "DensityInversion": DensityInversion,
    "DigitRollOver": DigitRollOver,
    "GlobalRange": GlobalRange,
    "Gradient": Gradient,
    "GradientDepthConditional": GradientDepthConditional,
    "LocationAtSea": LocationAtSea,
    "MonotonicZ": MonotonicZ,
    "ProfileEnvelop": ProfileEnvelop,
    "RateOfChange": RateOfChange,
    "RegionalRange": RegionalRange,
    "Spike": Spike,
    "SpikeDepthConditional": SpikeDepthConditional,
    "StuckValue": StuckValue,
    "Tukey53H": Tukey53H,
    "ValidGeolocation": ValidGeolocation,
    "WOA_NormBias": WOA_NormBias,
}


def catalog(klass):
    return QCTESTS.get(klass, klass)
