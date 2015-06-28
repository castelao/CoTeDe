# -*- coding: utf-8 -*-

"""
"""

from numpy import ma


def descentPrate(data):
    """

        It's probably a good idea to smooth it with a window of 2-5 seconds.
        After binned, the data will be probably groupped in bins of 1dbar,
          but the raw data might have more than one records per second, which
          might have plenty spikes. I'm looking here for inadequate casts
          lowered too fast, or maybe bad weather and a rolling vessel.

        Consider to create another test looking for excessive ups and downs.
    """
    assert ('timeS' in data), "timeS is not available"
    assert ('pressure' in data), "pressure is not available"
    assert data['timeS'].shape == data['pressure'].shape, \
            "t and p have different sizes"
    y = ma.masked_all(t.shape, dtype=t.dtype)
    dt = ma.diff(t)
    dp = ma.diff(p)
    y[1:] = dp/dt
    return y
