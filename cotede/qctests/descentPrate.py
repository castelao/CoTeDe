# -*- coding: utf-8 -*-

"""
"""

import logging

from numpy import ma


module_logger = logging.getLogger(__name__)

def descentPrate(data):
    """

        It's probably a good idea to smooth it with a window of 2-5 seconds.
        After binned, the data will be probably groupped in bins of 1dbar,
          but the raw data might have more than one records per second, which
          might have plenty spikes. I'm looking here for inadequate casts
          lowered too fast, or maybe bad weather and a rolling vessel.

        Consider to create another test looking for excessive ups and downs.
    """
    assert ('timeS' in data.keys()), "timeS is not available"
    assert ('PRES' in data.keys()), "pressure is not available"
    assert data['timeS'].shape == data['PRES'].shape, \
            "t and p have different sizes"
    dt = ma.diff(data['timeS'])
    dp = ma.diff(data['PRES'])
    y = ma.append(ma.fix_invalid(np.nan), dp/dt)
    return y
