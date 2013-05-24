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
