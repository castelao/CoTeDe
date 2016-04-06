# -*- coding: utf-8 -*-

import oceansdb

def location_at_sea(data, cfg=None):
    """ Evaluate if location is at sea.

        Interpolate the depth from ETOPO for the data position.
          If local "height" is negative, means lower than sea
          level, hence at sea.

        FIXME: It must allow to check Lat/Lon from data to work with
          TSGs, i.e. one location for each measurement.
          Double check other branches, I thought I had already done
            this before.
    """
    try:
        flag_bad = cfg['flag_bad']
    except:
        flag_bad = 3

    assert hasattr(data, 'attributes'), "Missing attributes"

    # Temporary solution while migrating to OceanSites variables syntax
    if ('LATITUDE' not in data.attributes) and \
            ('latitude' in data.attributes):
                print("Deprecated. In the future it will not accept latitude anymore. It'll must be LATITUDE")
                data.attributes['LATITUDE'] = data.attributes['latitude']
    if ('LONGITUDE' not in data.attributes) and \
            ('longitude' in data.attributes):
                print("Deprecated. In the future it will not accept longitude anymore. It'll must be LONGITUDE")
                data.attributes['LONGITUDE'] = data.attributes['longitude']

    if ('LATITUDE' not in data.attributes) or \
            ('LONGITUDE' not in data.attributes):
                print("Missing geolocation (lat/lon)")
                return 0

    ETOPO = oceansdb.ETOPO()
    try:
        etopo = ETOPO.extract(
                var='elevation',
                lat=data.attributes['LATITUDE'],
                lon=data.attributes['LONGITUDE'])
    except:
        return 0

    if etopo['elevation'] <= 0:
        return 1
    elif etopo['elevation'] > 0:
        return flag_bad
