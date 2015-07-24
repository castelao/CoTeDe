#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Check anomaly detection QC test
"""

import numpy as np

from cotede.utils.supportdata import download_testdata
from cotede.qc import fProfileQC

def test():
    """ Only test if run. Must improve this.
    """
    datafile = download_testdata("dPIRX010.cnv")
    pqc = fProfileQC(datafile, cfg='anomaly_detection')
    assert sorted(np.unique(pqc.flags['TEMP']['anomaly_detection'])) == [1,4]
