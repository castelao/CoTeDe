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
    for v in ['TEMP', 'PSAL']:
        assert v in pqc.keys()
        assert len(pqc[v]) == 1034
        assert v in pqc.flags
        for f in pqc.flags[v]:
            assert len(pqc.flags[v][f]) == 1034

    for a in ['datetime', 'LATITUDE', 'LONGITUDE']:
        assert a in pqc.attributes

    assert type(pqc.attributes['datetime']) == datetime
