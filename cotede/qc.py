""" Apply Quality Control of CTD profiles
"""

import pkg_resources
from datetime import datetime
from os.path import basename, expanduser
import re

import numpy as np
from numpy import ma

from seabird import cnv, CNVError

from cotede.qctests import *
from cotede.misc import combined_flag
from cotede.utils import get_depth_from_DAP
from cotede.utils import woa_profile_from_dap, woa_profile_from_file
from utils import make_file_list


class ProfileQC(object):
    """ Quality Control of a CTD profile
    """
    def __init__(self, input, cfg={}, saveauxiliary=True):
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

        self.name = 'ProfileQC'

        assert (hasattr(input, 'attributes'))
        assert (hasattr(input, 'keys')) and (len(input.keys()) > 0)
        assert (hasattr(input, 'data')) and (len(input.data) > 0)

        self.input = input
        self.attributes = input.attributes
        self.load_cfg(cfg)
        self.flags = {}
        self.saveauxiliary = saveauxiliary
        if saveauxiliary:
            #self.auxiliary = {}
            self.build_auxiliary()

        # I should use common or main, but must be consistent
        #   between defaults and flags.keys()
        # Think about it
        self.evaluate_common(self.cfg)

        for v in self.input.keys():
            for c in self.cfg.keys():
                if re.match("%s\d?$" % c, v):
                    print "evaluating: ", v, c
                    self.evaluate(v, self.cfg[c])
                    break

        # Evaluate twin sensors

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

        try:
            cfg_file = open(expanduser('~/.cotederc'))
        except IOError:
            self.cfg = eval(pkg_resources.resource_string(__name__, 'defaults'))
        else:
            configs = eval(cfg_file)

        for k in cfg:
            self.cfg[k] = cfg[k]

    def evaluate_common(self, cfg):
        self.flags['common'] = {}

        if 'valid_datetime' in self.cfg['main']:
            if 'datetime' in self.input.attributes.keys() and \
                    type(self.input.attributes['datetime']) == datetime:
                f = 1
            else:
                f = 3
            self.flags['common']['valid_datetime'] = f

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
                self.flags['common']['at_sea'] = depth[0]<0

        if self.saveauxiliary:
            self.auxiliary['common'] = {}
            self.auxiliary['common']['descentPrate'] = \
                    descentPrate(self['timeS'], self['pressure'])

    def evaluate(self, v, cfg):

        self.flags[v] = {}

        if self.saveauxiliary:
            if v not in self.auxiliary.keys():
                self.auxiliary[v] = {}

        if 'global_range' in cfg:
            self.flags[v]['global_range'] = np.zeros(self.input[v].shape,
                    dtype='i1')
            # Flag as 9 any masked input value
            self.flags[v]['global_range'][ma.getmaskarray(self.input[v])] = 9
            ind = (self.input[v] >= cfg['global_range']['minval']) & \
                    (self.input[v] <= cfg['global_range']['maxval'])
            self.flags[v]['global_range'][np.nonzero(ind)] = 1
            ind = (self.input[v] < cfg['global_range']['minval']) | \
                    (self.input[v] > cfg['global_range']['maxval'])
            self.flags[v]['global_range'][np.nonzero(ind)] = 4

        if 'gradient' in cfg:
            threshold = cfg['gradient']
            g = gradient(self.input[v])

            if self.saveauxiliary:
                self.auxiliary[v]['gradient'] = g

            flag = np.zeros(g.shape, dtype='i1')
            flag[self.input[v].mask == True] = 9
            flag[np.nonzero(g > threshold)] = 4
            flag[np.nonzero(g <= threshold)] = 1
            self.flags[v]['gradient'] = flag

        if 'gradient_depthconditional' in cfg:
            cfg_tmp = cfg['gradient_depthconditional']
            g = gradient(self.input[v])
            flag = np.zeros(g.shape, dtype='i1')
            # Flag as 9 any masked input value
            flag[ma.getmaskarray(self.input[v])] = 9
            # ---- Shallow zone -----------------
            threshold = cfg_tmp['shallow_max']
            flag[np.nonzero( \
                    (self['pressure'] <= cfg_tmp['pressure_threshold']) & \
                    (g > threshold))] \
                    = 4
            flag[np.nonzero( \
                    (self['pressure'] <= cfg_tmp['pressure_threshold']) & \
                    (g <= threshold))] \
                    = 1
            # ---- Deep zone --------------------
            threshold = cfg_tmp['deep_max']
            flag[np.nonzero( \
                    (self['pressure'] > cfg_tmp['pressure_threshold']) & \
                    (g > threshold))] \
                    = 4
            flag[np.nonzero( \
                    (self['pressure'] > cfg_tmp['pressure_threshold']) & \
                    (g <= threshold))] \
                    = 1

            self.flags[v]['gradient_depthconditional'] = flag

        if 'spike' in cfg:
            threshold = cfg['spike']
            s = spike(self.input[v])

            if self.saveauxiliary:
                self.auxiliary[v]['spike'] = s

            flag = np.zeros(s.shape, dtype='i1')
            # Flag as 9 any masked input value
            flag[ma.getmaskarray(self.input[v])] = 9
            flag[np.nonzero(s > threshold)] = 4
            flag[np.nonzero(s <= threshold)] = 1
            self.flags[v]['spike'] = flag

        if 'spike_depthconditional' in cfg:
            cfg_tmp = cfg['spike_depthconditional']
            s = spike(self.input[v])
            flag = np.zeros(s.shape, dtype='i1')
            # Flag as 9 any masked input value
            flag[ma.getmaskarray(self.input[v])] = 9
            # ---- Shallow zone -----------------
            threshold = cfg_tmp['shallow_max']
            flag[np.nonzero( \
                    (self['pressure'] <= cfg_tmp['pressure_threshold']) & \
                    (g > threshold))] \
                    = 4
            flag[np.nonzero( \
                    (self['pressure'] <= cfg_tmp['pressure_threshold']) & \
                    (g <= threshold))] \
                    = 1
            # ---- Deep zone --------------------
            threshold = cfg_tmp['deep_max']
            flag[np.nonzero( \
                    (self['pressure'] > cfg_tmp['pressure_threshold']) & \
                    (g > threshold))] \
                    = 4
            flag[np.nonzero( \
                    (self['pressure'] > cfg_tmp['pressure_threshold']) & \
                    (g <= threshold))] \
                    = 1

            self.flags[v]['spike_depthconditional'] = flag

        if 'tukey53H_norm' in cfg:
            """

                I slightly modified the Goring & Nikora 2002. It is
                  expected that CTD profiles has a typical depth
                  structure, with a range between surface and bottom.
            """
            k = cfg['tukey53H_norm']['k']
            s = tukey53H_norm(self.input[v], k)

            if self.saveauxiliary:
                self.auxiliary[v]['tukey53H_norm'] = s

            flag = np.zeros(s.shape, dtype='i1')
            # Flag as 9 any masked input value
            flag[ma.getmaskarray(self.input[v])] = 9
            flag[np.nonzero(s > threshold)] = 4
            flag[np.nonzero(s <= threshold)] = 1
            self.flags[v]['tukey53H_norm'] = flag

        #if 'spike_depthsmooth' in cfg:
        #    from maud.window_func import _weight_hann as wfunc
        #    cfg_tmp = cfg['spike_depthsmooth']
        #    cfg_tmp['dzwindow'] = 10
        #    smooth = ma.masked_all(self.input[v].shape)
        #    z = ped['pressure']
        #    for i in range(len(self.input[v])):
        #        ind = np.nonzero(ma.absolute(z-z[i]) < \
        #                cfg_tmp['dzwindow'])[0]
        #        ind = ind[ind != i]
        #        w = wfunc(z[ind]-z[i], cfg_tmp['dzwindow'])
        #        smooth[i] = (T[ind]*w).sum()/w.sum()

        if 'digit_roll_over' in cfg:
            threshold = cfg['digit_roll_over']
            s = step(self.input[v])

            if self.saveauxiliary:
                self.auxiliary[v]['step'] = s

            flag = np.zeros(s.shape, dtype='i1')
            # Flag as 9 any masked input value
            flag[ma.getmaskarray(self.input[v])] = 9

            flag[np.nonzero(ma.absolute(s) > threshold)] = 4
            flag[np.nonzero(ma.absolute(s) <= threshold)] = 1

            self.flags[v]['digit_roll_over'] = flag

        if 'bin_spike' in cfg:
            bin = bin_spike(self.input[v], cfg['bin_spike'])

            if self.saveauxiliary:
                self.auxiliary[v]['bin_spike'] = bin

        if 'density_inversion' in cfg:
            threshold = cfg['density_inversion']
            ds = densitystep(self['salinity'], self['temperature'],
                    self['pressure'])

            if self.saveauxiliary:
                self.auxiliary[v]['density_step'] = ds

            flag = np.zeros(s.shape, dtype='i1')
            # Flag as 9 any masked input value
            flag[ma.getmaskarray(self.input[v])] = 9

            flag[np.nonzero(ds < threshold)] = 3 # I'm not sure to use 3 or 4.
            flag[np.nonzero(ds >= threshold)] = 1

            self.flags[v]['density_inversion'] = flag

        if 'woa_comparison' in cfg:

            try:
                woa = woa_profile_from_file(v,
                    self.input.attributes['datetime'],
                    self.input.attributes['latitude'],
                    self.input.attributes['longitude'],
                    self.input['pressure'],
                    cfg['woa_comparison'])
            except:
                try:
                    woa = woa_profile_from_dap(v,
                        self.input.attributes['datetime'],
                        self.input.attributes['latitude'],
                        self.input.attributes['longitude'],
                        self.input['pressure'],
                        cfg['woa_comparison'])
                except:
                    print "Couldn't make woa_comparison of %s" % v
                    return

            if woa is None:
                print "WOA is not available at this site"
                return

            woa_bias = ma.absolute(self.input[v] - woa['woa_an'])

            if self.saveauxiliary:
                for k in woa.keys():
                    self.auxiliary[v][k] = woa[k]
                self.auxiliary[v]['woa_bias'] = woa_bias
                self.auxiliary[v]['woa_relbias'] = woa_bias/woa['woa_sd']

            self.flags[v]['woa_comparison'] = np.zeros(self.input[v].shape,
                    dtype='i1')
            # Flag as 9 any masked input value
            self.flags[v]['woa_comparison'][ma.getmaskarray(self.input[v])] = 9

            ind = woa_bias/woa['woa_sd'] <= \
                    cfg['woa_comparison']['sigma_threshold']
            self.flags[v]['woa_comparison'][np.nonzero(ind)] = 1
            ind = woa_bias/woa['woa_sd'] > \
                    cfg['woa_comparison']['sigma_threshold']
            self.flags[v]['woa_comparison'][np.nonzero(ind)] = 3

        if 'pstep' in cfg:
            ind = np.isfinite(self.input[v])
            if self.saveauxiliary:
                self.auxiliary[v]['pstep'] = ma.concatenate(
                        [ma.masked_all(1),
                            np.diff(self.input['pressure'][ind])])

    def build_auxiliary(self):
        if not hasattr(self, 'auxiliary'):
            self.auxiliary = {}

        self.auxiliary['common'] = {}
        self.auxiliary['common']['descentPrate'] = \
            descentPrate(self['timeS'], self['pressure'])


class fProfileQC(ProfileQC):
    def __init__(self, inputfile, cfg={}, saveauxiliary=False, silent=False,
            verbose=True):
        self.name = 'fProfileQC'

        try:
            input = cnv.fCNV(inputfile)
        except CNVError as e:
            #self.attributes['filename'] = basename(inputfile)
            if verbose is True:
                print e.msg
            raise

        super(fProfileQC, self).__init__(input, cfg=cfg,
                saveauxiliary=saveauxiliary)


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
            f = combined_flag(self.flags[key])
            return ma.masked_array(self.input[key].data, mask=(f!=1))

        raise KeyError('%s not found' % key)


class ProfileQCCollection(object):
    """ Load a collection of ProfileQC from a directory
    """
    def __init__(self, inputdir, inputpattern=".*\.cnv",
            saveauxiliary=False, pandas=True):
        """
        """
        self.name = "ProfileQCCollection"

        if pandas is True:
            try:
                import pandas as pd
                self.pandas = True
            except:
                print "Sorry, I couldn't load pandas"
                return

        self.inputfiles = make_file_list(inputdir, inputpattern)

        self.data = None
        self.flags = {}
        if saveauxiliary is True:
            self.auxiliary = {}

        results = []

        for f in self.inputfiles:
            results.append(fProfileQC(f, {}, saveauxiliary, True))

        for r in results:
            p = r
            if hasattr(p, 'error'):
               print("Fail to evaluate")
               #print p.error['msg']
            else:
                print "Processing: %s" % f

                # ---- Dealing with the data ---------------------------------
                tmp = p.input.as_DataFrame()
                profileid = p.attributes['md5']
                tmp['profileid'] = profileid
                tmp['profilename'] = p.attributes['filename']
                tmp['id'] = id = tmp.index

                #tmp = pd.concat([ p.input.as_DataFrame(), pd.DataFrame({'profileid': nf}) ])
                #self.data = pd.concat([self.data, p.input.as_DataFrame()])
                self.data = pd.concat([self.data, tmp])

                # Dealing with the data
                #if 'timeS' in p.keys():
                #    ind = ~p['timeS'].mask
                #    d = ma.masked_all(p['timeS'].shape, dtype='O')
                #    d0 = p.input.attributes['datetime']
                #    d[ind] = ma.array([d0+timedelta(seconds=s) for s in p['timeS'][ind]])
                #else:
                #    d = p.input.attributes['datetime']
                #tmp = {'datetime': pd.Series(d)}
                #for k in p.keys():
                #    tmp[k] = pd.Series(p[k])

                # ---- Dealing with the flags --------------------------------
                for v in p.flags.keys():
                    if v not in self.flags:
                        self.flags[v] = None
                    tmp = p.flags[v]
                    tmp['id'], tmp['profileid'] = id, profileid
                    self.flags[v] = pd.concat([self.flags[v],
                        pd.DataFrame(tmp)])
                # ---- Dealing with the auxiliary -----------------------------
                if saveauxiliary is True:
                    for a in p.auxiliary.keys():
                        if a not in self.auxiliary:
                            self.auxiliary[a] = None
                        tmp = p.auxiliary[a]
                        tmp['id'], tmp['profileid'] = id, profileid
                        self.auxiliary[a] = pd.concat([self.auxiliary[a],
                            pd.DataFrame(tmp)])


    def save(self, filename):
        if self.pandas is True:
            self.data.to_hdf("%s_data.hdf" % filename, 'df')
            for k in self.flags.keys():
                self.flags[k].to_hdf("%s_flags_%s.hdf" % (filename, k), 'df')
            if not hasattr(self, 'auxiliary'):
                for k in self.auxiliary.keys():
                    self.auxiliary[k].to_hdf("%s_flags_%s.hdf" % (filename, k), 'df')


class CruiseQC(object):
    """ Quality Control of a group of CTD profiles
    """
    def __init__(self, inputdir, inputpattern="*.cnv", cfg={},
            saveauxiliary=False):
        """

            Pandas is probably what I'm looking for here
        """

        inputfiles = make_file_list(inputdir, inputpattern)

        self.data = []
        for f in inputfiles:
            try:
                print "Processing: %s" % f
                self.data.append(ProfileQC(cnv.fCNV(f), saveauxiliary=saveauxiliary))
            except:
                print "Couldn't load: %s" % f

    def build_flags(self):
        """
        """
        flags = {}
        #for k in self.data[0].flags:
        #    if type(cruise.data[0].flags[k]) == dict
        #    else
        #    flags
        #for p in self.data:
        #    for k in p.flags.keys():

    def build_auxiliary(self):
        """ Build the auxiliary products for each profile

            Estimate Gradient, Spike, Step, etc values for each profile
        """
        for i in range(len(self.data)):
            self.data[i].build_auxiliary()

        self.auxiliary = self.data[0].auxiliary.copy()
        for i in range(1, len(self.data)):
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
