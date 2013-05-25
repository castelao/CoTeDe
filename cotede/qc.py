""" Apply Quality Control of CTD profiles
"""

import pkg_resources

import numpy as np
from numpy import ma

class ProfileQC(object):
    """ Quality Control of a CTD profile
    """
    def __init__(self, data, cfg={}):
        """
            Input: dictionary with data.
                - pressure[\d]:
                - temperature[\d]: 
                - salinity[\d]: 

            cfg: config file with thresholds

            =======================
            - Must have a log system
            - Probably accept incomplete cfg. If some threshold is
                not defined, take the default value.
            - Is the best return another dictionary?
        """

        self.data = data
        self.load_cfg(cfg)
        self.flags = {}

        import pdb; pdb.set_trace()
        for v in self.data.keys():
            if v in self.cfg.keys():
                self.test_var(v)

        print self.flags

    def load_cfg(self, cfg):
        """ Load the user's config and the default values

            Need to think better what do I want here. The user
              should be able to choose which variables to evaluate.

            How to handle conflicts between user's cfg and default?
        """
        #defaults = pkg_resources.resource_listdir(__name__, 'defaults')
        self.cfg = eval(pkg_resources.resource_string(__name__, 'defaults'))
        for k in cfg:
            self.cfg[k] = cfg[k]

    def test_var(self, v):

        self.flags[v] = {}
        if 'global_range' in self.cfg[v]:
            f = (self.data[v] >= self.cfg[v]['global_range']['minval']) & (self.data[v] <= self.cfg[v]['global_range']['maxval'])
            self.flags[v]['global_range'] = f

        if 'gradient' in self.cfg[v]:
            threshold = self.cfg[v]['gradient']
            x = self.data[v]
            g = ma.masked_all(x.shape)
            g[1:-1] = np.abs(x[1:-1] - (x[:-2] + x[2:])/2.0)
            flag = ma.masked_all(x.shape, dtype=np.bool)
            flag[np.nonzero(g>threshold)] = False
            flag[np.nonzero(g<=threshold)] = True
            self.flags[v]['gradient'] = flag

        if 'spike' in self.cfg[v]:
            threshold = self.cfg[v]['spike']
            x = self.data[v]
            s = ma.masked_all(x.shape)
            s[1:-1] = np.abs(x[1:-1] - (x[:-2] + x[2:])/2.0) - np.abs((x[2:] - x[:-2])/2.0)
            flag = ma.masked_all(x.shape, dtype=np.bool)
            flag[np.nonzero(s>threshold)] = False
            flag[np.nonzero(s<=threshold)] = True
            self.flags[v]['spike'] = flag

        if 'digit_roll_over' in self.cfg[v]:
            threshold = self.cfg[v]['digit_roll_over']
            x = self.data[v]
            d = ma.masked_all(x.shape)
            step = ma.masked_all(x.shape, dtype=np.float)
            step[1:] = ma.absolute(ma.diff(x))
            flag = ma.masked_all(x.shape, dtype=np.bool)
            flag[ma.absolute(step)>threshold] = False
            flag[ma.absolute(step)<=threshold] = True
            self.flags[v]['digit_roll_over'] = flag
