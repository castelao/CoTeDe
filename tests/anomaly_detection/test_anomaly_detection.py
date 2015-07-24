#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Check density inversion QC test
"""

import tempfile
import shutil

import numpy as np
from numpy import ma

from cotede.utils.supportdata import download_testdata
from cotede.anomaly_detection import split_data_groups
from cotede.anomaly_detection import rank_files
from cotede.anomaly_detection import flags2bin
from cotede.anomaly_detection import estimate_p_optimal
from cotede.anomaly_detection import calibrate_anomaly_detection


datalist = ["dPIRX010.cnv", "PIRA001.cnv", "dPIRX003.cnv"]
INPUTFILES = [download_testdata(f) for f in datalist]


def test_flags2bin(n=100):
    flag = ma.concatenate([np.random.randint(0,5,n),
        ma.masked_all(2, dtype='int8')])

    binflags = flags2bin(flag)

    assert type(binflags) == ma.MaskedArray
    assert binflags.dtype == 'bool'
    assert binflags.shape == (n+2,)
    assert binflags.mask[flag.mask].all(), \
            "All masked flags records should be also masked at binflags"


def test_split_data_groups(n=100):
    flag = ma.concatenate([np.random.randint(0,5,n),
        ma.masked_all(2, dtype='int8')])

    indices = split_data_groups(flag)

    assert type(indices) is dict
    assert sorted(indices.keys()) == ['err', 'fit', 'test']
    for k in indices:
        indices[k].size == n
        assert indices[k].dtype == 'bool'
        # Necessarily each group have trues and falses
        assert indices[k].any(), "%s are all True" % k
        assert (~indices[k]).any(), "%s are all False" % k
        # Indices return only valid data. Ignore masked.
        assert ~flag[indices[k]].mask.any()

    # Fit group is all True, but err & test must have both
    assert sorted(np.unique(flag[indices['fit']])) == [1,2]
    for k in ['err', 'test']:
        assert sorted(np.unique(flag[indices[k]])) == [1,2,3,4]


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


def test_estimate_p_optimal(n=100):
    prob = -1e2*np.random.random(n)

    binflag = np.ones(n, dtype='bool')
    p, err = estimate_p_optimal(prob, binflag)
    assert p < prob.min()
    assert err == 0

    #binflag = np.zeros(n, dtype='bool')
    #p, err = estimate_p_optimal(prob, binflag)
    #assert p > prob.max()
    #assert err = 0


def test_calibrate_anomaly_detection():
    try:
        tmpdir = tempfile.mkdtemp()
        for f in INPUTFILES:
            shutil.copy(f, tmpdir)

        output = calibrate_anomaly_detection(tmpdir, 'TEMP', cfg='cotede')
    finally:
        shutil.rmtree(tmpdir)

    assert type(output) is dict
    assert sorted(output.keys()) == ['err', 'err_ratio', 'false_negative',
            'false_positive', 'p_optimal', 'params', 'prob']
