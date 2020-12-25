import numpy as np
from numpy import datetime64, timedelta64
import os.path

from cotede.utils import cotederc

try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from supportdata import download_file

    SUPPORTDATA_AVAILABLE = True
except ImportError:
    SUPPORTDATA_AVAILABLE = True


def load_ctd():
    """
    """
    DATA_URL = "https://raw.githubusercontent.com/castelao/dummy/main/dPIRX010.npz"
    DATA_HASH = "16de9b674e7dceb4ac24feedda58a3ab"

    filename = os.path.join(cotederc("sampledata"), "dPIRX010.npz")
    if not os.path.exists(filename):
        assert SUPPORTDATA_AVAILABLE, "Require package supportdata to download samples"
        download_file(cotederc("sampledata"), DATA_URL, md5hash=DATA_HASH)

    attrs = np.load(filename, allow_pickle=True)["attrs"]
    attrs = {a[0]: a[1] for a in attrs}

    varnames = np.load(filename, allow_pickle=True)["varnames"]
    values = np.load(filename, allow_pickle=True)["data"]
    data = {k: v for k, v in zip(varnames, values)}

    class CoTeDeDataModel(object):
        def __init__(self, attrs, data):
            self.attrs = attrs
            self.data = data
        def __getitem__(self, key):
            return self.data[key]
        def keys(self):
            return self.data.keys()

    output = CoTeDeDataModel(attrs, data)

    return output


def load_water_level(as_frame=False):
    """
    """
    DATA_URL = "https://raw.githubusercontent.com/castelao/dummy/main/NOS_8764227.npz"
    DATA_HASH = "7ec673d82e0e361acfc4075fe914dc7d"

    filename = os.path.join(cotederc("sampledata"), "NOS_8764227.npz")
    if not os.path.exists(filename):
        assert SUPPORTDATA_AVAILABLE, "Require package supportdata to download samples"
        download_file(cotederc("sampledata"), DATA_URL, md5hash=DATA_HASH)

    data = np.load(filename, allow_pickle=True)["water_level"]
    data = {
        "epoch": data[:, 0].astype("f"),
        "water_level": data[:, 1].astype("f"),
        "flagged": data[:, 2].astype("bool"),
    }
    data["time"] = datetime64("1970-01-01") + data["epoch"] * timedelta64(1, "s")
    if as_frame:
        data = pd.DataFrame(data)

    return data
