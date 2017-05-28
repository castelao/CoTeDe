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

            cfg: Check cotede.utils.load_cfg() for the possible input formats
                   for cfg.

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
                if re.match("(%s)2?$" % c, v):
                    logging.debug(" %s - evaluating: %s, as type: %s" %
                            (self.name, v, c))
                    self.evaluate(v, self.cfg[c])
                    break

    @property
    def data(self):
        return self.input.data

    @property
    def features(self):
        return self.auxiliary

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
            self.flags['common']['location_at_sea'] = location_at_sea(
                    self.input,
                    self.cfg['main']['location_at_sea'])

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

        # Apply common flag for all points.
        if 'common' in self.flags:
            N = self.input[v].shape
            for f in self.flags['common']:
                self.flags[v][f] = self.flags['common'][f] * \
                        np.ones(N, dtype='i1')

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
            self.flags[v]['global_range'] = global_range(
                    self.input, v, cfg['global_range'])

        if 'regional_range' in cfg:
            logging.warn("Sorry, I'm no ready to evaluate regional_range()")

        if 'pressure_increasing' in cfg:
            logging.warn("Sorry, I'm no ready to evaluate pressure_increasing()")

        if 'profile_envelop' in cfg:
            self.flags[v]['profile_envelop'] = profile_envelop(
                    self.input, cfg['profile_envelop'], v)

        if 'gradient' in cfg:
            y = Gradient(self.input, v, cfg['gradient'])
            y.test()

            if self.saveauxiliary:
                self.auxiliary[v]['gradient'] = y.features['gradient']

            self.flags[v]['gradient'] = y.flags['gradient']

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
            y = Spike(self.input, v, cfg['spike'])
            y.test()

            if self.saveauxiliary:
                self.auxiliary[v]['spike'] = y.features['spike']

            self.flags[v]['spike'] = y.flags['spike']

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
                    (s > threshold))] \
                    = 4
            flag[np.nonzero( \
                    (self['PRES'] <= cfg_tmp['pressure_threshold']) & \
                    (s <= threshold))] \
                    = 1
            # ---- Deep zone --------------------
            threshold = cfg_tmp['deep_max']
            flag[np.nonzero( \
                    (self['PRES'] > cfg_tmp['pressure_threshold']) & \
                    (s > threshold))] \
                    = 4
            flag[np.nonzero( \
                    (self['PRES'] > cfg_tmp['pressure_threshold']) & \
                    (s <= threshold))] \
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
            y = Tukey53H(self.input, v, cfg['tukey53H_norm'])
            y.test()

            if self.saveauxiliary:
                self.auxiliary[v]['tukey53H_norm'] = \
                        y.features['tukey53H_norm']

            self.flags[v]['tukey53H_norm'] = y.flags['tukey53H_norm']

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
            y = Bin_Spike(self.input, v, cfg['bin_spike'])
            # y.test()

            if self.saveauxiliary:
                self.auxiliary[v]['bin_spike'] = y.features['bin_spike']

            # self.flags[v]['bin_spike'] = y.flags['bin_spike']

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
            y = WOA_NormBias(self.input, v, cfg['woa_normbias'])
            #        self.attributes)
            y.test()

            if self.saveauxiliary:
                for f in y.features:
                    self.auxiliary[v][f] = y.features[f]

            self.flags[v]['woa_normbias'] = y.flags['woa_normbias']

        #if 'pstep' in cfg:
        #    ind = np.isfinite(self.input[v])
        #    ind = ma.getmaskarray(self.input[v])
        #    if self.saveauxiliary:
        #        self.auxiliary[v]['pstep'] = ma.concatenate(
        #                [ma.masked_all(1),
        #                    np.diff(self.input['PRES'][ind])])

        if 'rate_of_change' in cfg:
            self.flags[v]['rate_of_change'], RoC = \
                    rate_of_change(self.input, v, cfg['rate_of_change'])
            if self.saveauxiliary:
                self.auxiliary[v]['rate_of_change'] = RoC

        if 'cum_rate_of_change' in cfg:
            x = cum_rate_of_change(self.input, v,
                    cfg['cum_rate_of_change']['memory'])
            self.flags[v]['cum_rate_of_change'] = np.zeros(x.shape, dtype='i1')
            self.flags[v]['cum_rate_of_change'][
                    np.nonzero(x <= cfg['cum_rate_of_change']['threshold'])
                    ] = 1
            self.flags[v]['cum_rate_of_change'][
                    np.nonzero(x > cfg['cum_rate_of_change']['threshold'])
                    ] = 4
            self.flags[v]['cum_rate_of_change'][
                    ma.getmaskarray(self.input[v])] = 9

        # FIXME: the Anomaly Detection and Fuzzy require some features
        #   to be estimated previously. Generalize this.
        if 'anomaly_detection' in  cfg:
            features = {}
            for f in cfg['anomaly_detection']['features']:
                if f == 'spike':
                    features['spike'] = spike(self.input[v])
                elif f == 'gradient':
                    features['gradient'] = gradient(self.input[v])
                elif f == 'tukey53H_norm':
                    features['tukey53H_norm'] = tukey53H_norm(self.input[v])
                elif f == 'rate_of_change':
                    RoC = ma.masked_all_like(self.input[v])
                    RoC[1:] = ma.absolute(ma.diff(self.input[v]))
                    features['rate_of_change'] = RoC
                elif (f == 'woa_normbias'):
                    y = WOA_NormBias(self.input, v, {})
                    features['woa_normbias'] = \
                            np.abs(y.features['woa_normbias'])
                else:
                    logging.error("Sorry, I can't evaluate anomaly_detection with: %s" % f)

            self.flags[v]['anomaly_detection'] = \
                    anomaly_detection(features, cfg['anomaly_detection'])

        if 'morello2014' in cfg:
            self.flags[v]['morello2014'] = morello2014(
                    features=self.auxiliary[v],
                    cfg=cfg['morello2014'])

        if 'fuzzylogic' in  cfg:
            features = {}
            for f in cfg['fuzzylogic']['features']:
                if f == 'spike':
                    features['spike'] = spike(self.input[v])
                elif f == 'gradient':
                    features['gradient'] = gradient(self.input[v])
                elif f == 'tukey53H_norm':
                    features['tukey53H_norm'] = tukey53H_norm(self.input[v],
                            k=1.5)
                elif f == 'rate_of_change':
                    RoC = ma.masked_all_like(data[v])
                    RoC[1:] = ma.absolute(ma.diff(data[v]))
                    features['rate_of_change'] = RoC
                elif (f == 'woa_normbias'):
                    y = WOA_NormBias(self.input, v, {})
                    features['woa_normbias'] = \
                            np.abs(y.features['woa_normbias'])
                else:
                    logging.error("Sorry, I can't evaluate fuzzylogic with: %s" % f)

            self.flags[v]['fuzzylogic'] = fuzzylogic(
                    features=features,
                    cfg=cfg['fuzzylogic'])

        self.flags[v]['overall'] = combined_flag(self.flags[v])

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
    def __init__(self, inputfile, cfg=None, saveauxiliary=True, verbose=True,
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
            return ma.masked_array(self.input[key].data,
                    mask=(self.flags[key]['overall']!=1))

        raise KeyError('%s not found' % key)
