# -*- coding: utf-8 -*-

from cotede.utils import get_depth

def location_at_sea(data, cfg):
    """ Evaluate if location is at sea.

        Interpolate the depth from ETOPO for the data position.
          If local "height" is negative, means lower than sea
          level, hence at sea.

        FIXME: It must allow to check Lat/Lon from data to work with
          TSGs, i.e. one location for each measurement.
          Double check other branches, I thought I had already done
            this before.
    """
    assert hasattr(data, 'attributes'), "Missing attributes"

    # Temporary solution while migrating to OceanSites variables syntax
    if ('LATITUDE' not in data.attributes) and \
            ('latitude' in data.attributes):
                data.attributes['latitude'] = data.attributes['LATITUDE']
    if ('LONGITUDE' not in data.attributes) and \
            ('longitude' in data.attributes):
                data.attributes['longitude'] = data.attributes['LONGITUDE']

    assert ('LATITUDE' in data.attributes), \
            "Missing latitude in attributes"
    assert ('LONGITUDE' in data.attributes), \
            "Missing longitude in attributes"

    depth = get_depth(data.attributes['LATITUDE'],
            data.attributes['LONGITUDE'],
            cfg=cfg)

    if depth < 0:
        return 1

    elif depth >= 0:
        try:
            return cfg['flag_bad']
        except:
            # Default flag if fail
            return 4

    return 0
