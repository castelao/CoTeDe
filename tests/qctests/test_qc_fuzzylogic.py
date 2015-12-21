#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Check Fuzzy Logic QC test
"""

import numpy as np

from cotede.utils.supportdata import download_testdata
from cotede.qc import fProfileQC

def test():
    """ Only test if run. Must improve this.
    """
    datafile = download_testdata("dPIRX010.cnv")
    pqc = fProfileQC(datafile, cfg='morello2014', saveauxiliary=True)
    # While anomaly detection is limited to spike, gradient and tukey tests it
    #   will always return 0 for the first and last.
    assert sorted(np.unique(pqc.flags['TEMP']['fuzzylogic'])) == [0, 1, 2, 3]
    assert sorted(np.unique(pqc.flags['TEMP2']['fuzzylogic'])) == [1, 2]
    assert sorted(np.unique(pqc.flags['PSAL']['fuzzylogic'])) == [0, 1, 2, 3]
    assert sorted(np.unique(pqc.flags['PSAL2']['fuzzylogic'])) == [1, 2]
