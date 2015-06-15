# -*- coding: utf-8 -*-

from cotede.utils import get_depth

def location_at_sea(data, cfg):
    """ Evaluate if location is at sea.

        Interpolate the depth from ETOPO for the data position.
          If local "height" is negative, means lower than sea
          level, hence at sea.
    """
    assert hasattr(data, 'attributes'), "Missing attributes"
    assert ('latitude' in data.attributes), \
            "Missing latitude in attributes"
    assert ('longitude' in data.attributes), \
            "Missing longitude in attributes"

    depth = get_depth(data.attributes['latitude'],
            data.attributes['longitude'],
            cfg=cfg)

    if depth < 0:
        return 1
    elif flag >= 0:
        return 3
    else:
        return 0
