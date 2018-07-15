#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shutil
import tempfile
import os.path

from cotede.utils import download_testdata
#from cotede.utils import ProfilesQCCollection
from cotede.utils import ProfilesQCPandasCollection


datalist = ["dPIRX010.cnv", "PIRA001.cnv", "dPIRX003.cnv"]
INPUTFILES = [download_testdata(f) for f in datalist]


def check_profiles(profiles):
    #assert len(INPUTFILES) == len(profiles)
    for p in profiles:
        assert hasattr(p, 'keys')
        assert len(p.keys()) > 0
        assert hasattr(p, 'flags')
        assert len(p.flags.keys()) > 0


def test_ProfilesQCPandasCollection():
    try:
        tmpdir = tempfile.mkdtemp()
        for f in INPUTFILES:
            shutil.copy(f, tmpdir)

        profiles = ProfilesQCPandasCollection(tmpdir, cfg='cotede',
                saveauxiliary=True)
        #check_profiles(profiles)
        profiles = ProfilesQCPandasCollection(tmpdir, cfg='cotede',
                saveauxiliary=False)
        #check_profiles(profiles)

    finally:
        shutil.rmtree(tmpdir)

    assert not os.path.exists(tmpdir), "tmpdir wasn't deleted: %s" % tmpdir
