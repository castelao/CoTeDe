# -*- coding: utf-8 -*-

"""

    Where is this test from? GTSPP?
"""

import numpy as np
from numpy import ma


def profile_envelop(data, cfg, varname):
    """

        Probably not the best way to do this, but works for now.
    """
    #assert varname in data.keys()

    z = data['PRES']
    x = data[varname]

    flag = np.zeros(z.shape, dtype='i1')

    for layer in cfg:
        ind = np.nonzero(
                eval("(z %s) & (z %s)" % (layer[0], layer[1]))
                )[0]
        f = eval("(x[ind] > %s) & (x[ind] < %s)" % (layer[2], layer[3]))
                
        flag[ind[f == True]] = 1
        flag[ind[f == False]] = 4    
    
    flag[ma.getmaskarray(x)] = 9

    return flag
