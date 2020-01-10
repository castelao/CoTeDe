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

    cfg = fix_config(cfg)
    if "inherit" in cfg:
        if isinstance(cfg["inherit"], str):
            cfg["inherit"] = [cfg["inherit"]]
        for parent in cfg["inherit"]:
            cfg = inheritance(cfg, load_cfg(parent))

    return cfg


def fix_config(cfg):
    """Adjust the config to the latest standard, if necessary

       This function allows backward compatibility with old config descriptos
       updating them to the current standard.
    """
    if ('revision' in cfg) and (cfg['revision'] == '0.21'):
        return cfg

    if 'revision' not in cfg:
        cfg = convert_pre_to_021(cfg)

    return cfg


def convert_pre_to_021(cfg):
    """Convert config standard 0.20 into 0.21

       Revision 0.20 is the original standard, which lacked a revision.

       Variables moved from top level to inside item 'variables'.
       Ocean Sites nomenclature moved to CF standard vocabulary:
         - TEMP -> sea_water_temperature
         - PSAL -> sea_water_salinity
    """
    def label(v):
        """Convert Ocean Sites vocabulary to CF standard names
        """
        if v == 'PRES':
            return 'sea_water_pressure'
        if v == 'TEMP':
            return 'sea_water_temperature'
        elif v == 'PSAL':
            return 'sea_water_salinity'
        else:
            return v

    keys = list(cfg.keys())

    output = OrderedDict()
    output['revision'] = '0.21'

    if 'inherit' in keys:
        output['inherit'] = cfg['inherit']
        keys.remove('inherit')

    if 'main' in cfg:
        output['common'] = cfg['main']
        keys.remove('main')
    elif 'common' in cfg:
        output['common'] = cfg['common']
        keys.remove('common')

    output['variables'] = OrderedDict()
    for k in keys:
        output['variables'][label(k)] = cfg[k]
        # output[k] = cfg[k]

    return output
