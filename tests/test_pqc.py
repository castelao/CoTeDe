# I should split in two tests, one for generic expected proprieties and
#   contents, and another test for specific contents, like keys, and values
#   itself. But this last one must require a md5.

import numpy as np
from seabird import cnv
import cotede.qc
from cotede.utils import download_testdata
from cotede.misc import combined_flag


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
    vs = list(pqc.flags.keys())
    vs.remove('common')
    for v in vs:
        for f in pqc.flags[v]:
            assert pqc.flags[v][f].dtype == 'i1'

    assert hasattr(pqc, 'auxiliary')
    assert type(pqc.auxiliary) is dict


def test_all_valid_no_9():
    """ If all measurements are valid it can't return flag 9

        This is to test a special condition when all values are valid, .mask
          return False, instead of an array on the same size with False.

        This test input all valid values, and check if there is no flag 9.
    """
    datafile = download_testdata("dPIRX010.cnv")
    pqc = cotede.qc.fProfileQC(datafile)
    assert pqc['TEMP'].mask.all() == False
    assert ~(combined_flag(pqc.flags['TEMP']) == 9).any()
