# I should split in two tests, one for generic expected proprieties and
#   contents, and another test for specific contents, like keys, and values
#   itself. But this last one must require a md5.

import numpy as np
from seabird import cnv
import cotede.qc
from cotede.utils.supportdata import download_testdata

def func(datafile, saveauxiliary):
    data = cnv.fCNV(datafile)
    pqc = cotede.qc.ProfileQC(data, saveauxiliary=saveauxiliary)
    return pqc


def test_answer():
    datafile = download_testdata("dPIRX010.cnv")

    pqc = func(datafile=datafile, saveauxiliary=False)

    pqc = func(datafile=datafile, saveauxiliary=True)

    keys = ['timeS', 'PRES', 'TEMP', 'TEMP2', 'CNDC', 'CNDC2',
            'potemperature', 'potemperature2', 'PSAL',
            'PSAL2', 'flag']
    assert pqc.keys() == keys
    assert len(pqc.attributes) == 13

    assert hasattr(pqc, 'flags')
    assert type(pqc.flags) is dict
    vs = pqc.flags.keys()
    vs.remove('common')
    for v in vs:
        for f in pqc.flags[v]:
            assert pqc.flags[v][f].dtype == 'i1'

    assert hasattr(pqc, 'auxiliary')
    assert type(pqc.auxiliary) is dict
