#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Check if pickle can serialize seabird's data objects

"""

import pickle

from seabird import cnv

from cotede.utils import download_testdata
from cotede.qc import ProfileQC, fProfileQC


datalist = ["dPIRX010.cnv", "PIRA001.cnv", "dPIRX003.cnv"]
INPUTFILES = [download_testdata(f) for f in datalist]


def test_serialize_ProfileQC():
        """ Serialize ProfileQC
        """
        for datafile in INPUTFILES:
            data = cnv.fCNV(datafile)
            pqc = ProfileQC(data, saveauxiliary=False)
            pqc2 = pickle.loads(pickle.dumps(pqc))
            assert pqc.attributes == pqc2.attributes
            #assert (profile.data == profile.data)


def test_serialize_fProfileQC():
        """ Serialize fProfileQC
        """
        for datafile in INPUTFILES:
            pqc = fProfileQC(datafile, saveauxiliary=False)
            pqc2 = pickle.loads(pickle.dumps(pqc))
            assert pqc.attributes == pqc2.attributes
            #assert (profile.data == profile.data)
