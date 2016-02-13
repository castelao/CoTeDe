#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Check Fuzzy Logic QC test
"""

import numpy as np

from cotede.utils.supportdata import download_testdata
from cotede.qc import fProfileQC

def test():
    """ Only test if run. Must improve this.

        ATENTION, this is sensitive to package WOA. Once I improve that
          package, the flags here might change, since several 2, 3 and 4
          flags are due the WOA climatology test.
    """
    datafile = download_testdata("dPIRX010.cnv")
    pqc = fProfileQC(datafile, cfg='morello2014')
    # While anomaly detection is limited to spike, gradient and tukey tests it
    #   will always return 0 for the first and last.
    assert sorted(np.unique(pqc.flags['TEMP']['morello2014'])) == [1, 2, 3, 4]
    assert sorted(np.unique(pqc.flags['TEMP2']['morello2014'])) == [1]
    assert sorted(np.unique(pqc.flags['PSAL']['morello2014'])) == [1, 2, 4]
    assert sorted(np.unique(pqc.flags['PSAL2']['morello2014'])) == [1]
