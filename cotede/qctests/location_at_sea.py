# -*- coding: utf-8 -*-

from cotede.utils import get_depth

def location_at_sea(lat, lon, cfg):
    depth = get_depth(lat, lon, cfg=cfg)

    if depth < 0:
        return 1
    elif flag >= 0:
        return 3
    else:
        return 0
