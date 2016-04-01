#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Check Fuzzy Logic QC test
"""

import numpy as np

from cotede.utils.supportdata import download_testdata
from cotede.qc import fProfileQC

def test():
    """
    """
    datafile = download_testdata("dPIRX010.cnv")
    pqc = fProfileQC(datafile, cfg='fuzzylogic')
    assert 'fuzzylogic' in pqc.flags['TEMP']
    assert sorted(np.unique(pqc.flags['TEMP']['fuzzylogic'])) == [1, 2, 4]
    assert sorted(np.unique(pqc.flags['TEMP2']['fuzzylogic'])) == [1]
    assert sorted(np.unique(pqc.flags['PSAL']['fuzzylogic'])) == [1, 2, 4]
    assert sorted(np.unique(pqc.flags['PSAL2']['fuzzylogic'])) == [1]
