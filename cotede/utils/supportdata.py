# -*- coding: utf-8 -*-

"""

#http://www.ngdc.noaa.gov/mgg/global/relief/ETOPO1/data/bedrock/grid_registered/netcdf/ETOPO1_Bed_g_gmt4.grd.gz

supportdata.download_file('http://opendap.ccst.inpe.br/Climatologies/ETOPO/etopo5.cdf','309bef6916aee6e12563d3f8c1f27503')
"""

import urllib2
import hashlib
import os
import shutil
from tempfile import NamedTemporaryFile

def download_file(url, md5hash):
    """ Download data file from web

        IMPROVE it to automatically extract gz files
    """
    download_block_size = 2 ** 16

    assert type(md5hash) is str

    d = os.path.expanduser("~/.cotederc/data")
    if not os.path.exists(d):
        os.makedirs(d)

    fname = os.path.join(d, os.path.basename(url))
    assert not os.path.isfile(fname), "Already exist: %s" % fname

    remote = urllib2.urlopen(url)

    hash = hashlib.md5()

    with NamedTemporaryFile(delete=False) as f:
        try:
            bytes_read = 0
            block = remote.read(download_block_size)
            while block:
                f.write(block)
                hash.update(block)
                bytes_read += len(block)
                block = remote.read(download_block_size)
        except:
            if os.path.exists(f.name):
                os.remove(f.name)
                raise

    h = hash.hexdigest()
    if h != md5hash:
        os.remove(f.name)
        print("Downloaded file doesn't match.")
        return

    shutil.move(f.name, fname)

def download_supportdata():
    download_file('http://opendap.ccst.inpe.br/Climatologies/ETOPO/etopo5.cdf','309bef6916aee6e12563d3f8c1f27503')
