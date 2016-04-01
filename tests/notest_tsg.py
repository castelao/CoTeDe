import numpy as np

from seabird import cnv
import cotede.qc
from cotede.utils.supportdata import download_testdata


def test_tsg():
    """ I should think about a way to test if the output make sense.
    """

    datafile = download_testdata("TSG_PIR_001.cnv")
    data = cnv.fCNV(datafile)
    # Fails with configuration cotede. It's not ready to handle missing variable, like missing PRES.
    #pqc = cotede.qc.ProfileQC(data)
    pqc = cotede.qc.ProfileQC(data, cfg='tsg')
    assert len(pqc.flags) > 0

    #N = pqc['TEMP'].size
    #for f in pqc.cfg['TEMP'].keys():
    #    pqc.flags['TEMP'][f].size == N
