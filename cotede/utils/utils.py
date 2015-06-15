import os
from os.path import expanduser
import re

import numpy as np
from numpy import ma

try:
    import netCDF4
except:
    print("netCDF4 is not available")

try:
    from pydap.client import open_url
    import pydap.lib
    pydap.lib.CACHE = '.cache'
except:
    print("PyDAP is not available")

from scipy.interpolate import RectBivariateSpline, interp1d


def make_file_list(inputdir, inputpattern):
    """ Search inputdir recursively for inputpattern
    """
    inputfiles = []
    for dirpath, dirnames, filenames in os.walk(inputdir):
        for filename in filenames:
            if re.match(inputpattern, filename):
                inputfiles.append(os.path.join(dirpath, filename))
    inputfiles.sort()
    return inputfiles


def get_depth(lat, lon, cfg):
    """

    ATTENTION, conceptual error on the data near by Greenwich.
    url='http://opendap.ccst.inpe.br/Climatologies/ETOPO/etopo5.cdf'

    If I ever need to get depth from multiple points, check the history
      of this file. One day it was like that.
    """
    assert type(lat) in [int, float]
    assert type(lon) in [int, float]

    # if lat.shape != lon.shape:
    #            print "lat and lon must have the same size"

    try:
        try:
            etopo = netCDF4.Dataset(expanduser(cfg['file']))
        except:
            etopo = netCDF4.Dataset(expanduser(cfg['url']))
        x = etopo.variables['ETOPO05_X'][:]
        y = etopo.variables['ETOPO05_Y'][:]
    except:
        etopo = open_url(cfg['url']).ROSE
        x = etopo.ETOPO05_X[:]
        y = etopo.ETOPO05_Y[:]

    if lon < 0:
        lon += 360

    iini = (abs(lon - x)).argmin() - 2
    ifin = (abs(lon - x)).argmin() + 2
    jini = (abs(lat - y)).argmin() - 2
    jfin = (abs(lat - y)).argmin() + 2

    assert (iini >= 0) or (iini <= len(x)) or \
        (jini >= 0) or (jini <= len(y)), \
        "Sorry not ready to handle too close to boundaries"

    try:
        z = etopo.variables['ROSE'][jini:jfin, iini:ifin]
    except:
        z = etopo.ROSE[jini:jfin, iini:ifin]

    interpolator = RectBivariateSpline(x[iini:ifin], y[jini:jfin], z.T)
    return interpolator(lon, lat)[0][0]


# ============================================================================
def savePQCCollection_pandas(db, filename):
    """ Save

        To Do:
            - Save the files in a tmp file
            - As it saves, creates a md5 of each file
            - Put everything together in a tar.bz2, including the md5 list
            - Delete the tmp file
    """
    import os
    import tempfile
    import tarfile
    import shutil
    import hashlib
    # tar = tarfile.open("%s.tar.bz2" % filename, "w:bz2")
    tar = tarfile.open(filename, "w:bz2")
    tmpdir = tempfile.mkdtemp()

    try:
        # Data
        f = "%s/data.hdf" % (tmpdir)
        db.data.to_hdf(f, 'df')
        tar.add(f, arcname='data.hdf')
        # hashlib.md5(open(f, 'rb').read()).digest()
        # hashlib.sha256(open(f, 'rb').read()).digest()
        # Flags
        p = os.path.join(tmpdir, 'flags')
        os.mkdir(p)
        for k in db.flags.keys():
            f = os.path.join(p, "flags_%s.hdf" % k)
            db.flags[k].to_hdf(f, 'df')
            tar.add(f, arcname="flags/flags_%s.hdf" % k)
        if hasattr(db, 'auxiliary'):
            p = os.path.join(tmpdir, 'aux')
            os.mkdir(p)
            for k in db.auxiliary.keys():
                f = os.path.join(p, "aux_%s.hdf" % k)
                db.auxiliary[k].to_hdf(f, 'df')
                tar.add(f, arcname="aux/aux_%s.hdf" % k)
        tar.close()
    except:
        shutil.rmtree(tmpdir)
        raise
        print "Problems saving the data"
        shutil.rmtree("%s.tar.bz2" % filename)
    finally:
        shutil.rmtree(tmpdir)
