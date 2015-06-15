""" Apply Quality Control of CTD profiles
"""

import pkg_resources
from datetime import datetime
from os.path import basename, expanduser
import re
import json
import logging

import numpy as np
from numpy import ma

from seabird import cnv, CNVError
from seabird.utils import basic_logger
logging.basicConfig(level=logging.DEBUG)

from cotede.qctests import *
from cotede.misc import combined_flag
from cotede.utils import get_depth, woa_profile


class ProfileQC(object):
    """ Quality Control of a CTD profile
    """
    def __init__(self, input, cfg=None, saveauxiliary=True, verbose=True,
            attributes=None, logger=None):
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
        self.logger = logger or logging.getLogger(__name__)

        self.name = input.filename
        self.verbose = verbose

        if attributes is None:
            assert (hasattr(input, 'attributes'))
        assert (hasattr(input, 'keys')) and (len(input.keys()) > 0)

        self.load_cfg(cfg)

        self.input = input
        if attributes is None:
            self.attributes = input.attributes
        else:
            self.attributes = attributes
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
                        self.logger.debug(" %s - evaluating: %s, as type: %s" %
                                (self.name, v, c))
                    self.evaluate(v, self.cfg[c])
                    break

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
            self.logger.debug("%s - User's QC cfg." % self.name)
            return

        # Need to safe_eval before allow to load rules from .cotederc
        if cfg is None:
            cfg = 'cotede'

        # If it's a name of a config, try to get from CoTeDe's package
        try:
            self.cfg = json.loads(pkg_resources.resource_string(__name__,
                "qc_cfg/%s" % cfg))
            if self.verbose is True:
                self.logger.debug("%s - QC cfg: %s" % (self.name, cfg))
        # If can't find inside cotede, try to load from users directory
        except:
            self.cfg = json.loads(expanduser('~/.cotederc/%s' % cfg))
            if self.verbose is True:
                self.logger.debug("%s - QC cfg: ~/.cotederc/%s" %
                        (self.name, cfg))

    def evaluate_common(self, cfg):
        if 'main' not in self.cfg.keys():
            self.logger.warn("ATTENTION, there is no main setup in the QC cfg")
            return

        self.flags['common'] = {}

        if 'valid_datetime' in self.cfg['main']:
            if 'datetime' in self.attributes.keys() and \
                    type(self.attributes['datetime']) == datetime:
                f = 1
            else:
                f = 3
            self.flags['common']['valid_datetime'] = f

        if 'datetime_range' in self.cfg['main']:
            if 'datetime' in self.attributes.keys() and \
                    (self.attributes['datetime'] >=
                            self.cfg['main']['datetime_range']['minval']) and \
                    (self.attributes['datetime'] <=
                            self.cfg['main']['datetime_range']['maxval']):
                f = 1
            else:
                f = 3
            self.flags['common']['datetime_range'] = f

        if 'at_sea' in self.cfg['main']:
            self.flags['common']['at_sea'] = location_at_sea(
                    self.input,
                    self.cfg['main']['at_sea'])

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
                    self.attributes['datetime'],
                    self.attributes['latitude'],
                    self.attributes['longitude'],
                    self.input['pressure'],
                    cfg['woa_comparison'])

            if woa is None:
                self.logger.warn("%s - WOA is not available at this site" %
                        self.name)
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
    """ Apply ProfileQC straight from a file.
    """
    def __init__(self, inputfile, cfg=None, saveauxiliary=False, verbose=True,
            logger=None):
        """
        """
        self.logger = logger or logging.getLogger(__name__)
        self.name = 'fProfileQC'

        try:
            # Not the best way, but will work for now. I should pass
            #   the reference for the logger being used.
            input = cnv.fCNV(inputfile, logger=None)
        except CNVError as e:
            #self.attributes['filename'] = basename(inputfile)
            self.logger.error(e.msg)
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
