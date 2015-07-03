
import numpy as np
from cotede.utils.supportdata import download_testdata

def func(datafile):
    from seabird import cnv
    import cotede.qc
    data = cnv.fCNV(datafile)
    ped = cotede.qc.ProfileQCed(data)
    return ped


def test_answer():
    datafile = download_testdata("dPIRX010.cnv")
    ped = func(datafile=datafile)
    keys = ['timeS', 'PRES', 'TEMP', 'TEMP2', 'CNDC', 'CNDC2',
            'potemperature', 'potemperature2', 'PSAL', 'PSAL2',
            'flag']
    assert ped.keys() == keys
    assert len(ped.attributes) == 13
