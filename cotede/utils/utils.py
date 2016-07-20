import os
from os.path import expanduser
import re
import pkg_resources
import json


def cotede_dir():
    return expanduser(os.getenv('COTEDE_DIR', '~/.cotederc'))

def make_file_list(inputdir, inputpattern):
    """ Search inputdir recursively for inputpattern
    """
    inputfiles = []
    for dirpath, dirnames, filenames in os.walk(inputdir):
        for filename in filenames:
            if re.match(inputpattern, filename):
                inputfiles.append(os.path.join(dirpath, filename))
    inputfiles.sort()
    return inputfiles


# ============================================================================
def savePQCCollection_pandas(db, filename):
    """ Save

        To Do:
            - Save the files in a tmp file
            - As it saves, creates a md5 of each file
            - Put everything together in a tar.bz2, including the md5 list
            - Delete the tmp file
    """
    import os
    import tempfile
    import tarfile
    import shutil
    import hashlib
    # tar = tarfile.open("%s.tar.bz2" % filename, "w:bz2")
    tar = tarfile.open(filename, "w:bz2")
    tmpdir = tempfile.mkdtemp()

    try:
        # Data
        f = "%s/data.hdf" % (tmpdir)
        db.data.to_hdf(f, 'df')
        tar.add(f, arcname='data.hdf')
        # hashlib.md5(open(f, 'rb').read()).digest()
        # hashlib.sha256(open(f, 'rb').read()).digest()
        # Flags
        p = os.path.join(tmpdir, 'flags')
        os.mkdir(p)
        for k in db.flags.keys():
            f = os.path.join(p, "flags_%s.hdf" % k)
            db.flags[k].to_hdf(f, 'df')
            tar.add(f, arcname="flags/flags_%s.hdf" % k)
        if hasattr(db, 'auxiliary'):
            p = os.path.join(tmpdir, 'aux')
            os.mkdir(p)
            for k in db.auxiliary.keys():
                f = os.path.join(p, "aux_%s.hdf" % k)
                db.auxiliary[k].to_hdf(f, 'df')
                tar.add(f, arcname="aux/aux_%s.hdf" % k)
        tar.close()
    except:
        shutil.rmtree(tmpdir)
        raise
        print("Problems saving the data")
        shutil.rmtree("%s.tar.bz2" % filename)
    finally:
        shutil.rmtree(tmpdir)


def load_cfg(cfg=None):
    """ Load the QC configurations

        The possible inputs are:
            - None: Will use the CoTeDe's default configuration

            - Config name [string]: A string with the name of a json file
                describing the QC procedure. It will first search among
                the build in pre-set (cotede, eurogoos, gtspp or argo),
                otherwise it will search in ~/.cotederc/cfg

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
        #self.cfg = cfg
        #self.logger.debug("%s - User's QC cfg." % self.name)
        return cfg

    if cfg is None:
        cfg = 'cotede'

    try:
        # If cfg is available in qc_cfg, use it
        cfg = json.loads(pkg_resources.resource_string('cotede',
            "qc_cfg/%s.json" % cfg))
        #self.logger.debug("%s - QC cfg: %s" % (self.name, cfg))
        return cfg
    except:
        # Otherwise, try to load from user's directory
        cfg = json.load(open(
            os.path.join(cotede_dir(), 'cfg/%s.json' % cfg)))
        #self.logger.debug("%s - QC cfg: ~/.cotederc/%s" %
        #            (self.name, cfg))
        return cfg
