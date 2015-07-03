import numpy as np

from seabird import cnv
import cotede.qc
from cotede.utils.supportdata import download_testdata


def test_multiple_cfg():
    """ I should think about a way to test if the output make sense.
    """

    datafile = download_testdata("dPIRX010.cnv")
    data = cnv.fCNV(datafile)
    pqc = cotede.qc.ProfileQC(data)
    pqc = cotede.qc.ProfileQC(data, cfg='cotede')
    pqc = cotede.qc.ProfileQC(data, cfg='gtspp')
    # Manually defined
    pqc = cotede.qc.ProfileQC(data, cfg={'TEMP': {"spike": 6.0,}})
    assert len(pqc.flags) > 0
