""" Apply Quality Control of CTD profiles
"""

import pkg_resources
from datetime import datetime
from os.path import basename, expanduser
import re
import multiprocessing as mp
import time
import json

import numpy as np
from numpy import ma

from seabird import cnv, CNVError

from cotede.qctests import *
from cotede.misc import combined_flag
from cotede.utils import get_depth_from_URL, woa_profile
from utils import make_file_list


class ProfileQC(object):
    """ Quality Control of a CTD profile
    """
    def __init__(self, input, cfg=None, saveauxiliary=True, verbose=True):
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

        self.load_cfg(cfg)

        self.input = input
        self.attributes = input.attributes
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
                    if verbose is True:
                        print "evaluating: ", v, c
                    self.evaluate(v, self.cfg[c])
                    break

        # Evaluate twin sensors

    @property
    def data(self):
        return self.input.data

    def keys(self):
        """ Return the available keys in self.data
        """
        return self.input.keys()

    def __getitem__(self, key):
        """ Return the key array from self.data
        """
        return self.input[key]

    def load_cfg(self, cfg):
        """ Load the QC configurations

            The possible inputs are:
                - None: Will use the CoTeDe's default configuration

                - Preset config name [string]: A string with the name of
                    pre-set rules, like 'cotede', 'egoos' or 'gtspp'.

                - User configs [dict]: a dictionary composed by the variables
                    to be evaluated as keys, and inside it another dictionary
                    with the tests to perform as keys. example
                    {'main':{
                        'valid_datetime': None,
                        },
                    'temperature':{
                        'global_range':{
                            'minval': -2.5,
                            'maxval': 45,
                            },
                        },
                    }
        """
        # A given manual configuration has priority
        if type(cfg) is dict:
            self.cfg = cfg
            print("User's QC cfg.")
            return

        # Need to safe_eval before allow to load rules from .cotederc
        if cfg is None:
            cfg = 'cotede'

        # If it's a name of a config, try to get from CoTeDe's package
        try:
            self.cfg = json.loads(pkg_resources.resource_string(__name__,
                "qc_cfg/%s" % cfg))
            print("QC cfg: %s" % cfg)
        # If can't find inside cotede, try to load from users directory
        except:
            self.cfg = json.loads(expanduser('~/.cotederc/%s' % cfg))
            print("QC cfg: ~/.cotederc/%s" % cfg)

    def evaluate_common(self, cfg):
        if 'main' not in self.cfg.keys():
            print("ATENTION, there is no main setup in the QC cfg")
            return

        self.flags['common'] = {}

        if 'valid_datetime' in self.cfg['main']:
            if 'datetime' in self.input.attributes.keys() and \
                    type(self.input.attributes['datetime']) == datetime:
                f = 1
            else:
                f = 3
            self.flags['common']['valid_datetime'] = f

        if 'datetime_range' in self.cfg['main']:
            if 'datetime' in self.input.attributes.keys() and \
                    (self.input.attributes['datetime'] >=
                            self.cfg['main']['datetime_range']['minval']) and \
                    (self.input.attributes['datetime'] <=
                            self.cfg['main']['datetime_range']['maxval']):
                f = 1
            else:
                f = 3
            self.flags['common']['datetime_range'] = f

        if 'at_sea' in self.cfg['main']:
            lon = self.input.attributes['longitude']
            lat = self.input.attributes['latitude']
            if 'url' in self.cfg['main']['at_sea']:
                depth = get_depth_from_URL(np.array([lat]),
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

        if 'profile_envelope' in cfg:
            # Probably not the best way to do this, but works for now.
            self.flags[v]['profile_envelope'] = np.zeros(self.input[v].shape,
                    dtype='i1')
            for layer in cfg['profile_envelope']:
                ind = np.nonzero(
                        eval("(%s %s) & (%s %s)" %
                            ("self.input['pressure']", layer[0],
                                "self.input['pressure']", layer[1]))
                            )[0]
                f = eval("(%s > %s) & (%s < %s)" %
                        ("self.input[v][ind]", layer[2],
                        "self.input[v][ind]", layer[3]))
                self.flags[v]['profile_envelope'][ind[f == True]] = 1
                self.flags[v]['profile_envelope'][ind[f == False]] = 4

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
            woa = woa_profile(v,
                    self.input.attributes['datetime'],
                    self.input.attributes['latitude'],
                    self.input.attributes['longitude'],
                    self.input['pressure'],
                    cfg['woa_comparison'])

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
    def __init__(self, inputfile, cfg=None, saveauxiliary=False, verbose=True):
        self.name = 'fProfileQC'

        try:
            input = cnv.fCNV(inputfile)
        except CNVError as e:
            #self.attributes['filename'] = basename(inputfile)
            if verbose is True:
                print e.msg
            raise

        super(fProfileQC, self).__init__(input, cfg=cfg,
                saveauxiliary=saveauxiliary, verbose=verbose)


class ProfileQCed(ProfileQC):
    """
    """
    def __init__(self, input, cfg=None):
        """
        """
        self.name = 'ProfileQCed'
        super(ProfileQCed, self).__init__(input, cfg)

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


def process_profiles_serial(inputfiles, cfg=None, saveauxiliary=False,
        verbose=True):
    """ Quality control a list of CTD files
    """
    profiles = []
    for f in inputfiles:
        try:
            p = fProfileQC(f, cfg, saveauxiliary, verbose=verbose)
            profiles.append(p)
        except CNVError as e:
            #print e.msg
            pass
    return profiles


def process_profiles(inputfiles, cfg=None, saveauxiliary=True,
        verbose=True, timeout=60):
    """ Quality control a list of CTD files in parallel
    """
    npes = 2 * mp.cpu_count()
    npes = min(npes, len(inputfiles))
    pool = mp.Pool(npes)
    queuesize = 3*npes
    qout = mp.Queue(queuesize)
    teste = []

    def run_qc(inputfiles, cfg, saveauxiliary, verbose):
        def process_file(f, cfg, saveauxiliary, verbose=verbose):
            try:
                if verbose is True:
                    print("Loading: %s" % f)
                p = fProfileQC(f, cfg, saveauxiliary, verbose)
                attrs = [pn.attributes for pn in p.data]
                qout.put([p, attrs], block=True)
            except CNVError as e:
                print e.msg

        pool = []
        for f in inputfiles[:npes]:
            pool.append(mp.Process(target=process_file,
                args=(f, cfg, saveauxiliary, verbose)))
            pool[-1].start()

        for i, f in enumerate(inputfiles[npes:]):
            n = i%npes
            pool[n].join(timeout)
            if pool[n].is_alive():
                print("timeout: %s" % pool[n])
            pool[n].terminate()
            pool[n] = mp.Process(target=process_file,
                args=(f, cfg, saveauxiliary, verbose))
            pool[n].start()

        for p in pool:
            p.join(timeout)
            if p.is_alive():
                print("timeout: %s" % p)
            p.terminate()
        print "Done evaluating."

    worker = mp.Process(target=run_qc,
            args=(inputfiles, cfg, saveauxiliary, verbose))
    worker.start()

    profiles = []
    while worker.is_alive() or not qout.empty():
        if qout.empty():
            #print("Queue is empty. I'll give a break.")
            time.sleep(2)
        else:
            # Dummy way to fix pickling on Queue
            # When the fProfile object is sent through the Queue, each
            #   data loses its .attributes.
            # Improve this in the future.
            out, attrs = qout.get()
            for i, a in enumerate(attrs):
                out.data[i].attributes = a
            print("Collected: %s" % out.attributes['filename'])
            profiles.append(out)

    worker.terminate()
    return profiles


class ProfileQCCollection(object):
    """ Load a collection of ProfileQC from a directory
    """
    def __init__(self, inputdir, inputpattern=".*\.cnv",
            cfg=None, saveauxiliary=False, timeout=60):
        """
        """
        self.name = "ProfileQCCollection"

        self.inputfiles = make_file_list(inputdir, inputpattern)

        self.data = None
        self.flags = {}
        if saveauxiliary is True:
            self.auxiliary = {}

        self.profiles = process_profiles(self.inputfiles, cfg, saveauxiliary,
                timeout=timeout)
        #self.profiles = process_profiles_serial(self.inputfiles, cfg,
        #        saveauxiliary)

        import pandas as pd
        for p in self.profiles:
                # ---- Dealing with the data ---------------------------------
                tmp = p.input.as_DataFrame()
                profileid = p.attributes['md5']
                tmp['profileid'] = profileid
                tmp['profilename'] = p.attributes['filename']
                tmp['id'] = id = tmp.index

                self.data = pd.concat([self.data, tmp])

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
    def __init__(self, inputdir, inputpattern="*.cnv", cfg=None,
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
