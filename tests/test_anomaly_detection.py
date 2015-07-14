#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Check density inversion QC test
"""


import numpy as np

from cotede.anomaly_detection import split_data_groups


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
