# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
"""

import pkg_resources
import json

import numpy as np

import cotede.qc
from cotede.qc import ProfileQC

from data import DummyData


def test_cfg_json():
    """ All config files should comply with json format

        In the future, when move load cfg outside, refactor here.
    """
    cfgfiles = [f for f in
            pkg_resources.resource_listdir('cotede', 'qc_cfg')
            if f[-5:] == ".json"]

    for cfgfile in cfgfiles:
        try:
            cfg = json.loads(pkg_resources.resource_string('cotede',
                        "qc_cfg/%s" % cfgfile))
        except:
            assert False, "Failed to load %s" % cfgfile

        assert isinstance(cfg, dict)
        for k in cfg.keys():
            assert len(cfg[k]) > 0


def test_cfg_existentprocedure():
    """ Check if all procedures requested by the cfg are available.
    """
    cfgfiles = [f for f in
            pkg_resources.resource_listdir('cotede', 'qc_cfg')
            if f[-5:] == ".json"]
    QCTESTS = dir(cotede.qctests)
    for cfgfile in cfgfiles:
        cfg = json.loads(pkg_resources.resource_string('cotede',
                        "qc_cfg/%s" % cfgfile))
        assert type(cfg) is dict
        for v in cfg.keys():
            for c in cfg[v]:
                assert c in QCTESTS, \
                        "Test %s.%s.%s is not available at cotede.qctests" % \
                        (cfgfile[:-5], v, c)


def test_multiple_cfg():
    """ I should think about a way to test if the output make sense.
    """
    profile = DummyData()
    for cfg in [None, 'cotede', 'gtspp', 'eurogoos']:
        pqc = cotede.qc.ProfileQC(profile, cfg=cfg)
        assert sorted(pqc.flags.keys()) == \
                ['PSAL', 'TEMP', 'common'], \
                "Incomplete flagging for %s: %s" % (cfg, pqc.flags.keys())
                # ['PSAL', 'PSAL2', 'TEMP', 'TEMP2', 'common'], \

    # Manually defined
    pqc = cotede.qc.ProfileQC(profile, cfg={
        "main": {},
        "TEMP": {"spike": {"threshold": 6.0,}}})
    assert sorted(pqc.flags['TEMP'].keys()) == ['overall', 'spike']
