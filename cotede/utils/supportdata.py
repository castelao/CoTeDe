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

    hash = hashlib.md5()

    fname = os.path.join(d, os.path.basename(url))
    if os.path.isfile(fname):
        h = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        if h == md5hash:
            print("Was previously downloaded: %s" % fname)
            return
        else:
            assert False, "%s already exist but doesn't match the hash: %s" % \
                    (fname, md5hash)

    remote = urllib2.urlopen(url)

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
        print("Downloaded file doesn't match. %s" % h)
        assert False, "Downloaded file (%s) doesn't match with expected hash (%s)" % \
                (fname, md5hash)

    shutil.move(f.name, fname)
    print("Downloaded: %s" % fname)

def download_supportdata():
    print("This can take several minutes, depending on the network bandwidth. Sorry, in the future I'll include a progress bar.")
    download_file('http://opendap.ccst.inpe.br/Climatologies/ETOPO/etopo5.cdf','309bef6916aee6e12563d3f8c1f27503')
    download_file('http://data.nodc.noaa.gov/thredds/fileServer/woa/WOA09/NetCDFdata/temperature_seasonal_5deg.nc','271f66e8dea4dfef7db99f5f411af330')
    download_file('http://data.nodc.noaa.gov/thredds/fileServer/woa/WOA09/NetCDFdata/salinity_seasonal_5deg.nc','1d2d1982338c688bdd18069d030ec05f')

def download_testdata(filename):

    #d = os.path.expanduser("~/.cotederc/testdata")
    d = os.path.expanduser("~/.cotederc/data")
    if not os.path.exists(d):
        os.makedirs(d)

    test_files = {
            'dPIRX010.cnv': {
                "url": "https://dl.dropboxusercontent.com/u/26063625/seabird/dPIRX010.cnv",
                "md5": "8691409accb534c83c8bd412afbdd285"},
            'dPIRX003.cnv': {
                "url": "https://dl.dropboxusercontent.com/u/26063625/seabird/dPIRX003.cnv",
                "md5": "4b941b902a3aea7d99e1cf4c78c51877"},
            'PIRA001.cnv': {
                "url": "https://dl.dropboxusercontent.com/u/26063625/seabird/PIRA001.cnv",
                "md5": "5ded777144300b63c8775b1d7f033f92"},
            'TSG_PIR_001.cnv': {
                "url": "https://dl.dropboxusercontent.com/u/26063625/seabird/TSG_PIR_001.cnv",
                "md5": "2950ccb9f77e0802557b011c63d2e39b"},
            }

    assert filename in test_files.keys(), \
            "%s is not a valid test file" % filename

    download_file(test_files[filename]["url"], test_files[filename]["md5"])
    datafile = os.path.join(os.path.expanduser("~/.cotederc/data/"),
            filename)

    return datafile
