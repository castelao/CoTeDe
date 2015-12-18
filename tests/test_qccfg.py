
import pkg_resources
import json

import numpy as np

from seabird import cnv
import cotede.qc
from cotede.utils.supportdata import download_testdata


def test_cfg_json():
    """ All config files should comply with json format

        In the future, when move load cfg outside, refactor here.
    """
    cfgfiles = [f for f in
            pkg_resources.resource_listdir('cotede', 'qc_cfg')
            if f[-5:] == ".json"]

    for cfgfile in cfgfiles:
        cfg = json.loads(pkg_resources.resource_string('cotede',
                        "qc_cfg/%s" % cfgfile))

        assert type(cfg) is dict
        for k in cfg.keys():
            assert len(cfg[k]) > 0


def test_multiple_cfg():
    """ I should think about a way to test if the output make sense.
    """

    datafile = download_testdata("dPIRX010.cnv")
    data = cnv.fCNV(datafile)
    pqc = cotede.qc.ProfileQC(data)
    pqc = cotede.qc.ProfileQC(data, cfg='cotede')
    pqc = cotede.qc.ProfileQC(data, cfg='gtspp')
    pqc = cotede.qc.ProfileQC(data, cfg='eurogoos')
    # Manually defined
    pqc = cotede.qc.ProfileQC(data, cfg={'TEMP': {"spike": 6.0,}})
    assert len(pqc.flags) > 0
