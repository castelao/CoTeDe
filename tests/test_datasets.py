# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst


from cotede import ProfileQC
import cotede.datasets


def test_load_ctd():
    """Load CTD sample dataset
    """
    ctd_dataset = cotede.datasets.load_ctd()
    ctd_dataset.keys()
    varnames = [
        "timeS",
        "PRES",
        "TEMP",
        "TEMP2",
        "CNDC",
        "CNDC2",
        "potemperature",
        "potemperature2",
        "PSAL",
        "PSAL2",
        "flag",
    ]
    for v in varnames:
        assert v in ctd_dataset.keys()
        assert len(ctd_dataset[v]) == 1014


def test_load_water_level():
    """Load water level sample dataset
    """
    water_level_dataset = cotede.datasets.load_water_level()
    water_level_dataset.keys()
    varnames = ["epoch", "water_level", "flagged", "time"]
    for v in varnames:
        assert v in water_level_dataset.keys()
        assert len(water_level_dataset[v]) == 21900


def test_qc_sample_ctd():
    """Guarantee that ProfileQC can run with a sample dataset

    Note
    ----
    - Assume that global_range will be always a default test.
    """
    data = cotede.datasets.load_ctd()
    pqc = ProfileQC(data)
    # Silly test. The most important is if the previous line didn't crash.
    assert len(pqc.flags["TEMP"]) > 0
    assert len(pqc.flags["TEMP"]["global_range"]) > 0
