# -*- coding: utf-8 -*-

""" Functions to handle a collection of profiles
"""

import time
# import logging
import multiprocessing as mp

import numpy as np
from numpy import ma

from seabird.exceptions import CNVError

from cotede.utils import make_file_list
#from cotede.qc import fProfileQC
import cotede.qc


def process_profiles_serial(inputfiles, cfg=None, saveauxiliary=False,
        verbose=True):
#                verbose=True, logger=None):
    """ Quality control a list of CTD files
    """
#    logger = logger or logging.getLogger(__name__)

    profiles = []
    for f in inputfiles:
        try:
            p = cotede.qc.fProfileQC(f, cfg, saveauxiliary, verbose=verbose)
            profiles.append(p)
        except CNVError as e:
            print(e.msg)
#            logger.warn(e.msg)

    return profiles


def process_profiles(inputfiles, cfg=None, saveauxiliary=True,
        verbose=True, timeout=60):
    # verbose=True, timeout=60, logger=None):
    """ Quality control a list of CTD files in parallel
    """
    # logger = logger or logging.getLogger(__name__)
    npes = 2 * mp.cpu_count()
    npes = min(npes, len(inputfiles))
    # logger.debug("Running with %s npes" % npes)
    queuesize = 3*npes
    # logger.debug("queue size: %s" % queuesize)
    qout = mp.Queue(queuesize)
    teste = []

    def run_qc(inputfiles, cfg, saveauxiliary, verbose):
        def process_file(f, cfg, saveauxiliary, verbose=verbose):
            try:
                if verbose is True:
                    print("Loading: %s" % f)
#                logger.debug("fProfileQC: %s" % f)
                p = cotede.qc.fProfileQC(f, cfg, saveauxiliary, verbose)
#                logger=logger)
                attrs = [pn.attributes for pn in p.data]
#                logger.debug("Sending profile %s to queue" % f)
                qout.put([p, attrs], block=True)
#                logger.debug("Sent to queue")
            except CNVError as e:
                print(e.msg)
#                logger.warn(e.msg)

        pool = []
        for f in inputfiles[:npes]:
            pool.append(mp.Process(target=process_file,
                args=(f, cfg, saveauxiliary, verbose)))
            pool[-1].start()

        for i, f in enumerate(inputfiles[npes:]):
            n = i % npes
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
        print("Done evaluating.")

    worker = mp.Process(target=run_qc,
            args=(inputfiles, cfg, saveauxiliary, verbose))
    worker.start()

    profiles = []
    while worker.is_alive() or not qout.empty():
        if qout.empty():
            # logger.debug("Queue is empty. I'll give a break.")
            # print("Queue is empty. I'll give a break.")
            time.sleep(2)
        else:
            # logger.debug("There are results waiting in queue")
            # Dummy way to fix pickling on Queue
            # When the fProfile object is sent through the Queue, each
            #   data loses its .attributes.
            # Improve this in the future.
            out, attrs = qout.get()
            for i, a in enumerate(attrs):
                out.data[i].attributes = a
            print("Collected: %s" % out.attributes['filename'])
            profiles.append(out)

    # logger.debug("Done. Worker finished and queue is empty")
    worker.terminate()
    return profiles


class ProfilesQCCollection(object):
    """ Load a collection of ProfileQC from a directory
    """
    def __init__(self, inputdir, inputpattern=".*\.cnv",
            cfg=None, saveauxiliary=False, timeout=60):
        """
        """
        self.name = "ProfilesQCCollection"

        self.inputfiles = make_file_list(inputdir, inputpattern)

        self.profiles = process_profiles(self.inputfiles, cfg, saveauxiliary,
                timeout=timeout)
        # self.profiles = process_profiles_serial(self.inputfiles, cfg,
        #        saveauxiliary)

        self.data = {'id': [], 'profileid': [], 'profilename': []}
        self.flags = {}
        if saveauxiliary is True:
            self.auxiliary = {}

        offset = 0
        for p in self.profiles:
            N = p['timeS'].size

            # Be sure that all have the same lenght.
            for v in p.keys():
                assert p[v].size == N
            ids = offset + np.arange(N)
            self.data['id'] = np.append(self.data['id'],
                    ids).astype('i')
            profileid = [p.attributes['md5']] * N
            self.data['profileid'] = np.append(self.data['profileid'],
                    profileid)
            profilename = [p.attributes['filename']] * N
            self.data['profilename'] = np.append(self.data['profilename'],
                    profilename)
            for v in p.keys():
                if v not in self.data:
                    self.data[v] = ma.masked_all(offset)
                self.data[v] = ma.append(self.data[v], p[v])

            # ---- Dealing with the flags --------------------------------
            for v in p.flags.keys():
                if v not in self.flags:
                    self.flags[v] = {'id': [], 'profileid': []}
                self.flags[v]['id'] = np.append(self.flags[v]['id'],
                        ids).astype('i')
                self.flags[v]['profileid'] = np.append(
                        self.flags[v]['profileid'], profileid)
                for t in p.flags[v]:
                    if t not in self.flags[v]:
                        self.flags[v][t] = ma.masked_all(offset)
                    self.flags[v][t] = ma.append(self.flags[v][t],
                            p.flags[v][t])
            offset += N

        return


class ProfilesQCPandasCollection(object):
    """ Quality Control a collection of ProfileQC from a directory

        Search all profiles inside the given directory and evaluate
          all them. The output is stored in a continuous table, where
          each profile receives a unique profileid value.

       This class was build thinking on join analysis of a batch of
         profiles, like all profiles from a specific cruise, for
         example.
    """
    def __init__(self, inputdir, inputpattern=".*\.cnv",
            cfg=None, saveauxiliary=False, timeout=60):
        """
        """
        try:
            import pandas as pd
        except:
            print("Pandas is not available.")
            return

        self.name = "ProfilesQCPandasCollection"

        self.inputfiles = make_file_list(inputdir, inputpattern)

        self.profiles = process_profiles(self.inputfiles, cfg, saveauxiliary,
                timeout=timeout)
        #self.profiles = process_profiles_serial(self.inputfiles, cfg,
        #        saveauxiliary)

        self.data = pd.DataFrame()
        self.flags = {}
        if saveauxiliary is True:
            self.auxiliary = {}

        for p in self.profiles:
            try:
                # ---- Dealing with the data ---------------------------------
                # FIXME: This expects a CNV object with as_DataFrame. I must
                #   generalize this.
                tmp = p.input.as_DataFrame()
                profileid = p.attributes['md5']
                tmp['profileid'] = profileid
                tmp['profilename'] = p.attributes['filename']
                cont_id = range(len(self.data), len(self.data)+len(tmp))
                tmp['id'] = cont_id
                tmp.set_index('id', inplace=True)

                self.data = pd.concat([self.data, tmp])

                # ---- Dealing with the flags --------------------------------
                V = [v for v in p.flags.keys() if v != 'common']
                for v in V:
                    tmp = pd.DataFrame(p.flags[v])
                    for f in p.flags['common']:
                        tmp[f] = p.flags['common'][f]

                    tmp['id'] = cont_id
                    tmp.set_index('id', inplace=True)

                    if v not in self.flags:
                        self.flags[v] = pd.DataFrame(tmp)
                    else:
                        self.flags[v] = pd.concat([self.flags[v],
                            pd.DataFrame(tmp)])
                # ---- Dealing with the auxiliary -----------------------------
                if saveauxiliary is True:
                    for a in p.auxiliary.keys():
                        tmp = pd.DataFrame(p.auxiliary[a])
                        tmp['id'] = cont_id
                        tmp.set_index('id', inplace=True)

                        if a not in self.auxiliary:
                            self.auxiliary[a] = pd.DataFrame(tmp)
                        else:
                            self.auxiliary[a] = pd.concat([self.auxiliary[a],
                                pd.DataFrame(tmp)])
            except:
                print("Failled")

    def keys(self):
        return [k for k in self.flags.keys()]

    def __getitem__(self, key):
        tmp = self.flags[key].copy()
        tmp[key] = self.data[key]
        tmp['timeS'] = self.data['timeS']
        tmp['PRES'] = self.data['PRES']
        return tmp

    def save(self, filename):
        store = pd.HDFStore(filename)
        # self.data.to_hdf("%s_data.hdf" % filename, 'df')
        store.append('data', self.data)
        for k in self.flags.keys():
            # self.flags[k].to_hdf("%s_flags_%s.hdf" % (filename, k), 'df')
            store.append("flags_%s" % k, self.flags[k])
        if hasattr(self, 'auxiliary'):
            for k in self.auxiliary.keys():
                # self.auxiliary[k].to_hdf("%s_flags_%s.hdf" % (filename, k), 'df')
                store.append("auxiliary_%s" % k, self.auxiliary[k])
