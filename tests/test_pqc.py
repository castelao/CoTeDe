# I should split in two tests, one for generic expected proprieties and
#   contents, and another test for specific contents, like keys, and values
#   itself. But this last one must require a md5.

import numpy as np

def func(datafile):
    from seabird import cnv
    import cotede.qc
    data = cnv.fCNV(datafile)
    pqc = cotede.qc.ProfileQC(data, saveauxiliary=True)
    return pqc


def test_answer():
    datafile = "./tests/dPIRX010.cnv"
    pqc = func(datafile=datafile)
    keys = ['timeS', 'pressure', 'temperature', 'temperature2', 'conductivity',
            'conductivity2', 'potemperature', 'potemperature2', 'salinity',
            'salinity2', 'flag']
    assert pqc.keys() == keys
    assert len(pqc.attributes) == 11
