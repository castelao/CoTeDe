
import numpy as np

def func(datafile):
    from seabird import cnv
    import cotede.qc
    data = cnv.fCNV(datafile)
    ped = cotede.qc.ProfileQCed(data)
    return ped


def test_answer():
    datafile = "./tests/dPIRX010.cnv"
    ped = func(datafile=datafile)
    keys = ['timeS', 'pressure', 'temperature', 'temperature2', 'conductivity',
            'conductivity2', 'potemperature', 'potemperature2', 'salinity',
            'salinity2', 'flag']
    assert ped.keys() == keys
    assert len(ped.attributes) == 11
