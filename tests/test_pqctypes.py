# I should split in two tests, one for generic expected proprieties and
#   contents, and another test for specific contents, like keys, and values
#   itself. But this last one must require a md5.

import numpy as np
from cotede.utils import download_testdata

def func(datafile):
    from seabird import cnv
    import cotede.qc
    data = cnv.fCNV(datafile)
    pqc = cotede.qc.ProfileQC(data, saveauxiliary=True)
    return pqc


def test_answer():
    datafile = download_testdata("dPIRX010.cnv")
    pqc = func(datafile=datafile)
    assert type(pqc.keys()) == list
    assert type(pqc.attributes) == dict
    assert hasattr(pqc, 'input')
    assert hasattr(pqc, 'flags')
    assert hasattr(pqc, 'auxiliary')
    assert type(pqc.flags) == dict
    for k in pqc.flags.keys():
        assert type(pqc.flags[k]) == dict
        for kk in pqc.flags[k].keys():
            assert (type(pqc.flags[k][kk]) == np.ndarray) or \
                (type(pqc.flags[k][kk]) == int)
            if (type(pqc.flags[k][kk]) == np.ndarray):
                assert pqc.flags[k][kk].dtype == 'int8'
