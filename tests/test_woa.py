""" Test World Ocean Atlas climatology access

    Initial prototype, still plenty to do here.
"""

from datetime import datetime
import numpy as np

from cotede.utils import woa
#from cotede.utils import supportdata
#supportdata.download_supportdata()


def test_woa_profile():
    woa.woa_profile(['temperature'], datetime.now(), 0, -35, np.array([100]),
            cfg={"file": "~/.cotederc/data/temperature_seasonal_5deg.nc",
                "vars": {"woa_an": "t_mn", "woa_sd": "t_sd", "woa_n": "t_dd"}}
            )


def test_woa_profile_from_file():
    woa.woa_profile_from_file(['temperature'], datetime.now(), 0, -35, np.array([100]),
            cfg={"file": "~/.cotederc/data/temperature_seasonal_5deg.nc",
                "vars": {"woa_an": "t_mn", "woa_sd": "t_sd", "woa_n": "t_dd"}}
            )
