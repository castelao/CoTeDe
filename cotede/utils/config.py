from collections import OrderedDict
import copy
import json
import os.path
import pkg_resources

from .utils import cotederc


def inheritance(child, parent):
    """Aggregate into child what is missing from parent
    """
    for v in child:
        if (v in parent) and isinstance(child[v], dict) and isinstance(parent[v], dict):
            parent[v] = inheritance(child[v], parent[v])
        else:
            parent[v] = child[v]
    return parent


def load_cfg(cfgname="cotede"):
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
    if cfgname is None:
        cfgname = "cotede"

    assert type(cfgname) in (dict, str), \
            'load_cfg() input must be a dictionary or a str'

    # A given manual configuration has priority
    if isinstance(cfgname, dict):
        # self.logger.debug("%s - User's QC cfg." % self.name)
        cfg = OrderedDict(copy.deepcopy(cfgname))
    elif isinstance(cfgname, str):
        try:
            # If cfg is available in qc_cfg, use it
            p = pkg_resources.resource_string(
                "cotede", os.path.join("qc_cfg", "{}.json".format(cfgname))
            )
            cfg = json.loads(p, object_pairs_hook=OrderedDict)
            # self.logger.debug("%s - QC cfg: %s" % (self.name, cfg))
        except:
            # Otherwise, try to load from user's directory
            p = os.path.join(cotederc(), "cfg", "{}.json".format(cfgname))
            with open(p, 'r') as f:
                cfg = json.load(f, object_pairs_hook=OrderedDict)
        # self.logger.debug("%s - QC cfg: ~/.cotederc/%s" %
        #            (self.name, cfg))

    if "inherit" in cfg:
        if isinstance(cfg["inherit"], str):
            cfg["inherit"] = [cfg["inherit"]]
        for parent in cfg["inherit"]:
            cfg = inheritance(cfg, load_cfg(parent))

    return cfg
