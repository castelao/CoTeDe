# Test to load an ARGO file

from datetime import datetime

from argo import argo
from cotede.qc import ProfileQC
#import cotede.qc
from cotede.utils.supportdata import download_testdata


def test_argo():
    datafile = download_testdata("20150127_prof.nc")

    profile = argo.profile_from_nc(datafile)[0]
    pqc = ProfileQC(profile, cfg='argo')

    print pqc.keys()
    print dir(pqc.input)
    print pqc.flags

    assert hasattr(pqc, 'flags')
    assert type(pqc.attributes['datetime']) == datetime
    assert 'TEMP' in pqc.keys()
