""" Apply Quality Control of CTD profiles
"""

import pkg_resources
from datetime import datetime
from os.path import basename
import re
import json
import logging

import numpy as np
from numpy import ma

from seabird import cnv
from seabird.exceptions import CNVError
#from seabird.utils import basic_logger
logging.basicConfig(level=logging.DEBUG)

from cotede.qctests import *
from cotede.misc import combined_flag
from cotede.utils import load_cfg


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
        #self.logger = logger or logging.getLogger(__name__)
        logging.getLogger(logger or __name__)

        try:
            self.name = input.filename
        except:
            self.name = None
        self.verbose = verbose

        if attributes is None:
            assert (hasattr(input, 'attributes'))
        assert (hasattr(input, 'keys')) and (len(input.keys()) > 0)

        self.cfg = load_cfg(cfg)

        self.input = input
        if attributes is None:
            self.attributes = input.attributes
        else:
            self.attributes = attributes
        self.flags = {}
        self.saveauxiliary = saveauxiliary
        if saveauxiliary:
            #self.auxiliary = {}
            # build_auxiliary is not exactly the best way to do it.
            self.build_auxiliary()

        # I should use common or main, but must be consistent
        #   between defaults and flags.keys()
        # Think about it
        self.evaluate_common(self.cfg)

        for v in self.input.keys():
            for c in self.cfg.keys():
                if re.match("%s\d?$" % c, v):
                    logging.debug(" %s - evaluating: %s, as type: %s" %
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

    def evaluate_common(self, cfg):
        if 'main' not in self.cfg.keys():
            logging.warn("ATTENTION, there is no main setup in the QC cfg")
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

        if 'location_at_sea' in self.cfg['main']:
            try:
                self.flags['common']['location_at_sea'] = location_at_sea(
                    self.input,
                    self.cfg['main']['location_at_sea'])
            except:
                print("Fail location_at_sea test")

        if self.saveauxiliary:
            self.auxiliary['common'] = {}
            # Need to improve this. descentPrate doesn't make sense
            #   for ARGO. That's why the try.
            try:
                self.auxiliary['common']['descentPrate'] = \
                        descentPrate(self.input)
            except:
                pass

    def evaluate(self, v, cfg):

        self.flags[v] = {}

        if self.saveauxiliary:
            if v not in self.auxiliary.keys():
                self.auxiliary[v] = {}

        if 'platform_identification' in cfg:
            logging.warn("Sorry I'm not ready to evaluate platform_identification()")

        if 'valid_geolocation' in cfg:
            logging.warn("Sorry I'm not ready to evaluate valid_geolocation()")

        if 'valid_speed' in cfg:
            # Think about. ARGO also has a test  valid_speed, but that is
            #   in respect to sucessive profiles. How is the best way to
            #   distinguish them here?
            try:
                if self.saveauxiliary:
                    self.flags[v]['valid_speed'], \
                            self.auxiliary[v]['valid_speed'] = \
                            possible_speed(self.input, cfg['valid_speed'])
            except:
                print("Fail on valid_speed")

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

        if 'regional_range' in cfg:
            logging.warn("Sorry, I'm no ready to evaluate regional_range()")

        if 'pressure_increasing' in cfg:
            logging.warn("Sorry, I'm no ready to evaluate pressure_increasing()")

        if 'profile_envelope' in cfg:
            self.flags[v]['profile_envelope'] = profile_envelope(
                    self.input, cfg['profile_envelope'], v)

        if 'gradient' in cfg:
            threshold = cfg['gradient']
            g = gradient(self.input[v])

            if self.saveauxiliary:
                self.auxiliary[v]['gradient'] = g

            flag = np.zeros(g.shape, dtype='i1')
            flag[ma.getmaskarray(self.input[v])] = 9
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
                    (self['PRES'] <= cfg_tmp['pressure_threshold']) & \
                    (g > threshold))] \
                    = 4
            flag[np.nonzero( \
                    (self['PRES'] <= cfg_tmp['pressure_threshold']) & \
                    (g <= threshold))] \
                    = 1
            # ---- Deep zone --------------------
            threshold = cfg_tmp['deep_max']
            flag[np.nonzero( \
                    (self['PRES'] > cfg_tmp['pressure_threshold']) & \
                    (g > threshold))] \
                    = 4
            flag[np.nonzero( \
                    (self['PRES'] > cfg_tmp['pressure_threshold']) & \
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
                    (self['PRES'] <= cfg_tmp['pressure_threshold']) & \
                    (g > threshold))] \
                    = 4
            flag[np.nonzero( \
                    (self['PRES'] <= cfg_tmp['pressure_threshold']) & \
                    (g <= threshold))] \
                    = 1
            # ---- Deep zone --------------------
            threshold = cfg_tmp['deep_max']
            flag[np.nonzero( \
                    (self['PRES'] > cfg_tmp['pressure_threshold']) & \
                    (g > threshold))] \
                    = 4
            flag[np.nonzero( \
                    (self['PRES'] > cfg_tmp['pressure_threshold']) & \
                    (g <= threshold))] \
                    = 1

            self.flags[v]['spike_depthconditional'] = flag

        if 'stuck_value' in cfg:
            logging.warn("Sorry I'm not ready to evaluate stuck_value()")

        if 'grey_list' in cfg:
            logging.warn("Sorry I'm not ready to evaluate grey_list()")

        if 'gross_sensor_drift' in cfg:
            logging.warn("Sorry I'm not ready to evaluate gross_sensor_drift()")

        if 'frozen_profile' in cfg:
            logging.warn("Sorry I'm not ready to evaluate frozen_profile()")

        if 'deepest_pressure' in cfg:
            logging.warn("Sorry I'm not ready to evaluate deepest_pressure()")

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

        # ARGO, test #12. (10C, 5PSU)
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
            try:
                if self.saveauxiliary:
                    self.flags[v]['density_inversion'], \
                            self.auxiliary[v]['density_step'] = \
                            density_inversion(
                                    self.input,
                                    cfg['density_inversion'],
                                    saveaux=True)
                else:
                    self.flags[v]['density_inversion'] = density_inversion(
                            self.input, cfg['density_inversion'])
            except:
                print("Fail on density_inversion")

        if 'woa_normbias' in cfg:
            if self.saveauxiliary:
                self.flags[v]['woa_normbias'], \
                        self.auxiliary[v]['woa_relbias'] = \
                        woa_normbias(self.input, v, cfg['woa_normbias'])
                #for k in woa.keys():
                #    self.auxiliary[v][k] = woa[k]
                #self.auxiliary[v]['woa_bias'] = woa_bias
                #self.auxiliary[v]['woa_relbias'] = woa_bias/woa['woa_sd']
            else:
                self.flags[v]['woa_normbias'], \
                        tmp = \
                        woa_normbias(self.input, v, cfg['woa_normbias'])
                del(tmp)

        #if 'pstep' in cfg:
        #    ind = np.isfinite(self.input[v])
        #    ind = ma.getmaskarray(self.input[v])
        #    if self.saveauxiliary:
        #        self.auxiliary[v]['pstep'] = ma.concatenate(
        #                [ma.masked_all(1),
        #                    np.diff(self.input['PRES'][ind])])

        if 'RoC' in cfg:
            x = ma.concatenate([ma.masked_all(1), ma.diff(self.input[v])])
            if self.saveauxiliary:
                self.auxiliary[v]['RoC'] = x
            self.flags[v]['RoC'] = np.zeros(x.shape, dtype='i1')
            self.flags[v]['RoC'][np.nonzero(x <= cfg['RoC'])] = 1
            self.flags[v]['RoC'][np.nonzero(x > cfg['RoC'])] = 4
            self.flags[v]['RoC'][ma.getmaskarray(self.input[v])] = 9

        if 'anomaly_detection' in  cfg:
            features = {}
            for f in cfg['anomaly_detection']['features']:
                if f == 'spike':
                    features['spike'] = spike(self.input[v])
                elif f == 'gradient':
                    features['gradient'] = gradient(self.input[v])
                elif f == 'tukey53H_norm':
                    features['tukey53H_norm'] = tukey53H_norm(self.input[v],
                            k=1.5)
                else:
                    logging.error("Sorry, I can't evaluate anomaly_detection with: %s" % f)

            self.flags[v]['anomaly_detection'] = \
                    anomaly_detection(features, cfg['anomaly_detection'])

        if 'fuzzylogic' in cfg:
            self.flags[v]['fuzzylogic'] = fuzzylogic(
                    self.auxiliary[v],
                    v,
                    cfg['fuzzylogic'])

    def build_auxiliary(self):
        if not hasattr(self, 'auxiliary'):
            self.auxiliary = {}

        self.auxiliary['common'] = {}
        try:
            self.auxiliary['common']['descentPrate'] = \
                    descentPrate(self.input)
        except:
            logging.warn("Failled to run descentPrate")


class fProfileQC(ProfileQC):
    """ Apply ProfileQC straight from a file.
    """
    def __init__(self, inputfile, cfg=None, saveauxiliary=False, verbose=True,
            logger=None):
        """
        """
        #self.logger = logger or logging.getLogger(__name__)
        logging.getLogger(logger or __name__)
        self.name = 'fProfileQC'

        try:
            # Not the best way, but will work for now. I should pass
            #   the reference for the logger being used.
            input = cnv.fCNV(inputfile, logger=None)
        except CNVError as e:
            #self.attributes['filename'] = basename(inputfile)
            logging.error(e.msg)
            raise

        super(fProfileQC, self).__init__(input, cfg=cfg,
                saveauxiliary=saveauxiliary, verbose=verbose,
                logger=logger)


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
