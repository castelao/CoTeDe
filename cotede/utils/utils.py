import os
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
                inputfiles.append(os.path.join(dirpath,filename))
    inputfiles.sort()
    return inputfiles

def get_depth_from_URL(lat, lon, url):
    """

    ATENTION, conceptual error on the data near by Greenwich.
    url='http://opendap.ccst.inpe.br/Climatologies/ETOPO/etopo5.cdf'
    """

    if lat.shape != lon.shape:
                print "lat and lon must have the same size"
    try:
        nc = netCDF4.Dataset(url)
        x = nc.variables['ETOPO05_X'][:]
        y = nc.variables['ETOPO05_Y'][:]
    except:
        dataset = open_url(url)
        etopo = dataset.ROSE
        x = etopo.ETOPO05_X[:]
        y = etopo.ETOPO05_Y[:]

    if lon.min()<0:
        ind = lon<0
        lon[ind] = lon[ind]+360
    iini = max(0, (np.absolute(lon.min()-x)).argmin()-2)
    ifin = (np.absolute(lon.max()-x)).argmin()+2
    jini = max(0, (np.absolute(lat.min()-y)).argmin()-2)
    jfin = (np.absolute(lat.max()-y)).argmin()+2

    try:
        z = nc.variables['ROSE'][jini:jfin, iini:ifin]
    except:
        z = etopo.ROSE[jini:jfin, iini:ifin]

    interpolator = RectBivariateSpline(x[iini:ifin], y[jini:jfin], z.T)
    depth = ma.array([interpolator(xx, yy)[0][0] for xx, yy in zip(lon,lat)])
    return depth


# ============================================================================
def savePQCCollection_pandas(db, filename):
    """ Save

        ToDo:
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
    #tar = tarfile.open("%s.tar.bz2" % filename, "w:bz2")
    tar = tarfile.open(filename, "w:bz2")
    tmpdir = tempfile.mkdtemp()

    try:
        # Data
        f = "%s/data.hdf" % (tmpdir)
        db.data.to_hdf(f, 'df')
        tar.add(f, arcname='data.hdf')
        #hashlib.md5(open(f, 'rb').read()).digest()
        #hashlib.sha256(open(f, 'rb').read()).digest()
        # Flags
        p = os.path.join(tmpdir,'flags')
        os.mkdir(p)
        for k in db.flags.keys():
            f = os.path.join(p, "flags_%s.hdf" % k)
            db.flags[k].to_hdf(f, 'df')
            tar.add(f, arcname="flags/flags_%s.hdf" % k)
        if hasattr(db, 'auxiliary'):
            p = os.path.join(tmpdir,'aux')
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
