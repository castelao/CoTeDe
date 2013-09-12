""" Apply Quality Control of CTD profiles
"""

import pkg_resources
from datetime import datetime

import numpy as np
from numpy import ma

from cotede.utils import get_depth_from_DAP
from cotede.utils import woa_profile_from_dap

class ProfileQC(object):
    """ Quality Control of a CTD profile
    """
    def __init__(self, input, cfg={}):
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

        self.input = input
        self.load_cfg(cfg)
        self.flags = {}

        if 'valid_datetime' in self.cfg['main']:
            self.flags['valid_datetime'] = \
                    type(self.input.attributes['datetime'])==datetime
        if 'at_sea' in self.cfg['main']:
            lon = self.input.attributes['longitude']
            lat = self.input.attributes['latitude']
            if 'url' in self.cfg['main']['at_sea']:
                depth = get_depth_from_DAP(np.array([lat]), 
                        np.array([lon]),
                        url=self.cfg['main']['at_sea']['url'])
                #flag[depth<0] = True
                #flag[depth>0] = False
                #self.flags['at_sea'] = flag
                self.flags['at_sea'] = depth[0]<0

        # Must have a better way to do this!
        import re
        for v in self.input.keys():
            c = re.sub('2$','', v)
            if c in self.cfg.keys():
                self.evaluate(v, self.cfg[c])

    def keys(self):
        """ Return the available keys in self.data
        """
        return self.input.keys()

    def __getitem__(self, key):
        """ Return the key array from self.data
        """
        return self.input[key]

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

    def evaluate(self, v, cfg):

        self.flags[v] = {}
        if 'global_range' in cfg:
            f = (self.input[v] >= cfg['global_range']['minval']) & (self.input[v] <= cfg['global_range']['maxval'])
            self.flags[v]['global_range'] = f

        if 'gradient' in cfg:
            threshold = cfg['gradient']
            #x = self.input[v]
            #g = ma.masked_all(x.shape)
            #g[1:-1] = np.abs(x[1:-1] - (x[:-2] + x[2:])/2.0)
            g = gradient(self.input[v])
            flag = ma.masked_all(g.shape, dtype=np.bool)
            flag[np.nonzero(g>threshold)] = False
            flag[np.nonzero(g<=threshold)] = True
            self.flags[v]['gradient'] = flag

        if 'spike' in cfg:
            threshold = cfg['spike']
            #x = self.input[v]
            #s = ma.masked_all(x.shape)
            #s[1:-1] = np.abs(x[1:-1] - (x[:-2] + x[2:])/2.0) - np.abs((x[2:] - x[:-2])/2.0)
            s = spike(self.input[v])
            flag = ma.masked_all(s.shape, dtype=np.bool)
            flag[np.nonzero(s>threshold)] = False
            flag[np.nonzero(s<=threshold)] = True
            self.flags[v]['spike'] = flag

        if 'digit_roll_over' in cfg:
            threshold = cfg['digit_roll_over']
            #x = self.input[v]
            #d = ma.masked_all(x.shape)
            #step = ma.masked_all(x.shape, dtype=np.float)
            #step[1:] = ma.absolute(ma.diff(x))
            s = step(self.input[v])
            flag = ma.masked_all(s.shape, dtype=np.bool)
            flag[ma.absolute(s)>threshold] = False
            flag[ma.absolute(s)<=threshold] = True
            self.flags[v]['digit_roll_over'] = flag

        if 'woa_comparison' in cfg:
            try:
                woa_an, woa_sd = woa_profile_from_dap(v, 
                    int(self.input.attributes['datetime'].strftime('%j')),
                    self.input.attributes['latitude'], 
                    self.input.attributes['longitude'], 
                    self.input['pressure'])
                woa_anom = (self.input[v] - woa_an) / woa_sd
                self.flags[v]['woa_comparison'] = \
                    woa_anom < 3
            except:
                print "Couldn't make woa_comparison of %s" % v

    def build_auxiliary(self):
        vars = ['temperature']
        products = ['step', 'gradient', 'spike']

        if not hasattr(self,'auxiliary'):
            self.auxiliary = {}

        for v in vars:
            if v not in self.auxiliary.keys():
                self.auxiliary[v] = {}

            for p in products:
                self.auxiliary[v][p] = eval("%s(self['%s'])" % (p,v))

        self.auxiliary['common'] = {}
        self.auxiliary['common']['descentPrate'] = \
            descentPrate(self['timeS'], self['pressure'])


class ProfileQCed(ProfileQC):
    """
    """
    def __init__(self, input, cfg={}):
        """
        """
        super(ProfileQCed, self).__init__(input, cfg)
        self.name = 'ProfileQCed'

    def keys(self):
        """ Return the available keys in self.data
        """
        return self.input.keys()

    def __getitem__(self, key):
        """ Return the key array from self.data
        """
        if key not in self.flags.keys():
            return self.input[key]
        else:
            f = ma.array([self.flags[key][f] for f in self.flags[key]]).T
            mask = self.input[key].mask | (~f).any(axis=1)
            return ma.masked_array(self.input[key].data, mask)

        raise KeyError('%s not found' % key)


inputdir = "/Users/castelao/Dropbox/work/piratadata/pirataxii/"
class CruiseQC(object):
    """ Quality Control of a group of CTD profiles
    """
    def __init__(self, inputdir, inputpattern = "*.cnv", cfg={}):
        """

            Pandas is probably what I'm looking for here
        """
        import glob
        from seabird import cnv
        inputfiles = glob.glob(inputdir+"*.cnv")
        inputfiles.sort()

        self.data = []
        for f in inputfiles:
            try:
                self.data.append(ProfileQC(cnv.fCNV(f)))
            except:
                print "Couldn't load: %s" % f

    def build_auxiliary(self):
        """ Build the auxiliary products for each profile

            Estimate Gradient, Spike, Step, etc values for each profile
        """
        for i in range(len(self.data)):
            self.data[i].build_auxiliary()

        self.auxiliary = self.data[0].auxiliary.copy()
        for i in range(1,len(self.data)):
            for k in self.data[i].auxiliary.keys():
                for kk in self.data[i].auxiliary[k].keys():
                    self.auxiliary[k][kk] = ma.concatenate(
                            [self.auxiliary[k][kk],
                            self.data[i].auxiliary[k][kk]])


    def keys(self):
        k = self.data[0].keys()
        #k.append('auxiliary')
        return k

    def __getitem__(self, key):
        output = self.data[0][key]
        for d in self.data[1:]:
            output = ma.concatenate([output, d[key]])

        return output






def step(x):
    y = ma.masked_all(x.shape, dtype = x.dtype)
    y[1:] = ma.diff(x)
    return y

def gradient(x):
    y = ma.masked_all(x.shape, dtype = x.dtype)
    y[1:-1] = np.abs(x[1:-1] - (x[:-2] + x[2:])/2.0)
    # ATENTION, temporary solution
    #y[0]=0; y[-1]=0
    return y

def spike(x):
    y = ma.masked_all(x.shape, dtype = x.dtype)
    y[1:-1] = np.abs(x[1:-1] - (x[:-2] + x[2:])/2.0) - \
                np.abs((x[2:] - x[:-2])/2.0)
    # ATENTION, temporary solution
    #y[0]=0; y[-1]=0
    return y

def descentPrate(t, p):
    assert t.shape == p.shape, "t and p have different sizes"
    y = ma.masked_all(t.shape, dtype = t.dtype)
    dt = ma.diff(t)
    dp = ma.diff(p)
    y[1:] = dp/dt
    return y
    
