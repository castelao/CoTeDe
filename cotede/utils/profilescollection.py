# -*- coding: utf-8 -*-

""" Functions to handle a collection of profiles
"""

import time
import multiprocessing as mp

from seabird import cnv, CNVError

from cotede.utils import make_file_list
#from cotede.qc import fProfileQC
import cotede.qc


def process_profiles_serial(inputfiles, cfg=None, saveauxiliary=False,
        verbose=True):
    """ Quality control a list of CTD files
    """
    profiles = []
    for f in inputfiles:
        try:
            p = cotede.qc.fProfileQC(f, cfg, saveauxiliary, verbose=verbose)
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
                p = cotede.qc.fProfileQC(f, cfg, saveauxiliary, verbose)
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


class ProfilesQCCollection(object):
    """ Load a collection of ProfileQC from a directory
    """
    def __init__(self, inputdir, inputpattern=".*\.cnv",
            cfg=None, saveauxiliary=False, timeout=60):
        """
        """
        self.name = "ProfilesQCCollection"

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
            try:
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
            except:
                print("Failled")

    def save(self, filename):
        import pandas
        store = pandas.HDFStore(filename)
        #self.data.to_hdf("%s_data.hdf" % filename, 'df')
        store.append('data', self.data)
        for k in self.flags.keys():
            #self.flags[k].to_hdf("%s_flags_%s.hdf" % (filename, k), 'df')
            store.append("flags_%s" % k, self.flags[k])
        if hasattr(self, 'auxiliary'):
            for k in self.auxiliary.keys():
                #self.auxiliary[k].to_hdf("%s_flags_%s.hdf" % (filename, k), 'df')
                store.append("auxiliary_%s" % k, self.auxiliary[k])


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
