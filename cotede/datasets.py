import numpy as np
from numpy import datetime64, timedelta64
import os.path

from cotede.utils import cotederc

try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


def load_water_level(as_frame=False):
    filename = os.path.join(cotederc("sampledata"), "NOS_8764227.npz")
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
