# -*- coding: utf-8 -*-

"""Utilities for CoTeDe

Miscelaneous resources to support CoTeDe.
"""

import os
from os.path import expanduser
import re
import pkg_resources
import json


def cotederc(subdir=None):
    """Directory with custom configuration for CoTeDe

    To keep the local environment tight, CoTeDe expects to find all local files,
    like pre-set QC procedures, in one single place. This function returns the
    path to that directory.

    Parameters
    ----------
    subdir : str, optional
        Sub-directory inside the base custom directory.

    Returns
    -------
    str
        A path to the local custom files.

        The default path is a directory at the user's home like::

            ~/.config/cotederc/

    Note
    ----
    That default path can be modified by defining the environment variable
    COTEDE_DIR. On bash that could be done like::

        export COTEDE_DIR='/my/other/awesome/path/'

    Note
    ----
    For windows users the path is automatically adjusted to reflect its
    syntax.

    Example
    -------
    A sub-directory for configuration files, named 'cfg', can be determined by::

    >>> cotederc('cfg')
    """
    path = os.getenv("COTEDE_DIR", os.path.join("~", ".config", "cotederc"))
    path = os.path.expanduser(path)
    if subdir is not None:
        path = os.path.join(path, subdir)
    return path


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
        db.data.to_hdf(f, "df")
        tar.add(f, arcname="data.hdf")
        # hashlib.md5(open(f, 'rb').read()).digest()
        # hashlib.sha256(open(f, 'rb').read()).digest()
        # Flags
        p = os.path.join(tmpdir, "flags")
        os.mkdir(p)
        for k in db.flags.keys():
            f = os.path.join(p, "flags_%s.hdf" % k)
            db.flags[k].to_hdf(f, "df")
            tar.add(f, arcname="flags/flags_%s.hdf" % k)
        if hasattr(db, "auxiliary"):
            p = os.path.join(tmpdir, "aux")
            os.mkdir(p)
            for k in db.auxiliary.keys():
                f = os.path.join(p, "aux_%s.hdf" % k)
                db.auxiliary[k].to_hdf(f, "df")
                tar.add(f, arcname="aux/aux_%s.hdf" % k)
        tar.close()
    except:
        shutil.rmtree(tmpdir)
        raise
        print("Problems saving the data")
        shutil.rmtree("%s.tar.bz2" % filename)
    finally:
        shutil.rmtree(tmpdir)


def loadPQCCollection_pandas(filename):
    import os
    import tempfile
    import tarfile
    import shutil

    tmpdir = tempfile.mkdtemp()
    tar = tarfile.open(filename, "r:*")
    tar.extractall(path=tmpdir)
    shutil.rmtree(tmpdir)
