#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cotede.utils.supportdata import download_testdata

from cotede.utils.profilescollection import process_profiles_serial
from cotede.utils.profilescollection import process_profiles


datalist = ["dPIRX010.cnv", "PIRA001.cnv", "dPIRX003.cnv"]
INPUTFILES = [download_testdata(f) for f in datalist]


def check_profiles(profiles):
    assert len(INPUTFILES) == len(profiles)
    for p in profiles:
        assert hasattr(p, 'keys')
        assert len(p.keys()) > 0
        assert hasattr(p, 'flags')
        assert len(p.flags.keys()) > 0


def test_process_profiles_serial():
    profiles = process_profiles_serial(INPUTFILES, saveauxiliary=False)
    check_profiles(profiles)
    profiles = process_profiles_serial(INPUTFILES, saveauxiliary=True)
    check_profiles(profiles)


def test_process_profiles():
    profiles = process_profiles(INPUTFILES, saveauxiliary=False)
    check_profiles(profiles)
    profiles = process_profiles(INPUTFILES, saveauxiliary=True)
    check_profiles(profiles)
