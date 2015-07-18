#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Check density inversion QC test
"""

import tempfile
import shutil

import numpy as np

from cotede.utils.supportdata import download_testdata
from cotede.anomaly_detection import split_data_groups
from cotede.anomaly_detection import rank_files


datalist = ["dPIRX010.cnv", "PIRA001.cnv", "dPIRX003.cnv"]
INPUTFILES = [download_testdata(f) for f in datalist]


def test_split_data_groups():
    ind = np.random.random(100) < 0.7
    indices = split_data_groups(ind)

    assert type(indices) is dict
    assert sorted(indices.keys()) == ['ind_err', 'ind_fit', 'ind_test']
    N = ind.size
    for k in indices:
        indices[k].size == N
        assert indices[k].any(), "%s are all True" % k
        assert (~indices[k]).any(), "%s are all False" % k


def test_rank_files():
    try:
        tmpdir = tempfile.mkdtemp()
        for f in INPUTFILES:
            shutil.copy(f, tmpdir)

        output = rank_files(tmpdir, 'TEMP', cfg='cotede')
    finally:
        shutil.rmtree(tmpdir)

    assert type(output) is list
    assert output == ['dPIRX010.cnv', 'dPIRX003.cnv', 'PIRA001.cnv']
