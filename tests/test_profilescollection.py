
import os

from cotede.utils.supportdata import download_testdata

from cotede.utils.profilescollection import process_profiles_serial
from cotede.utils.profilescollection import process_profiles
from cotede.utils import ProfilesQCCollection


def create_input_list():
    """
    """
    datalist = ["dPIRX010.cnv", "PIRA001.cnv", "dPIRX003.cnv"]
    return [download_testdata(f) for f in datalist]


def test_process_profiles_serial():
    inputfiles = create_input_list()
    profiles = process_profiles_serial(inputfiles, saveauxiliary=False)
    profiles = process_profiles_serial(inputfiles, saveauxiliary=True)


def test_process_profiles():
    inputfiles = create_input_list()
    profiles = process_profiles(inputfiles, saveauxiliary=False)
    profiles = process_profiles(inputfiles, saveauxiliary=True)


def test_ProfilesQCCollection():
    inputfiles = create_input_list()
    inputdir = os.path.dirname(inputfiles[0])
    profiles = ProfilesQCCollection(inputdir, saveauxiliary=False)
    profiles = ProfilesQCCollection(inputdir, saveauxiliary=True)
