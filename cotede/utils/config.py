# -*- coding: utf-8 -*-

"""Resources related to QC configuration
"""

from collections import OrderedDict
import copy
import json
import os.path
import pkg_resources

from .utils import cotederc


def list_cfgs():
    """List the available QC procedures, builtin + local

    Full QC procedures, defining which tests and respective parameters to be
    used, can be saved to be re-used later. Several procedures are built-in
    CoTeDe, but the user can create its own collection. This function returns
    a list of all procedures available, built-in + the local user collection.

    See also
    --------
    utils.load_cfg
    """
    cfg = pkg_resources.resource_listdir('cotede', "qc_cfg")
    cfg = sorted([c[:-5] for c in cfg if c[-5:] == ".json"])

    ucfg = os.listdir(cotederc("cfg"))
    ucfg = [c[:-5] for c in ucfg if c[-5:] == ".json"]
    ucfg = [c for c in ucfg if c not in cfg]

    cfg.extend(sorted(ucfg))

    return cfg


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
    """Load a QC configuration

    A QC procedure is a sequence of tests, and respective tuning parameters
    used to quality control a dataset. This is how the user controls the
    QC steps to apply.

    Parameters
    ----------
    cfgname : string or dict-list, optional

        - None: If not given, it will use the CoTeDe's default configuration,
          which is equivalent to use cfgname='cotede'.

        - A config name [string]: A string with the name of a json file
          describing the QC procedure. It will first search among the build
          in pre-set (ex.: cotede, eurogoos, gtspp, argo, ...). If can't find
          a config with that name, it will search at ~/.config/cotederc/cfg/,
          or the path defined by the local variable $COTEDE_DIR.

        - Inline config [dict-like]: A dictionary describing the variables to
          process and which tests to use on each one. A minimalist example to
          apply the gradient test in the sea water temperature could be:

              >>> {"sea_water_temperature": {"gradient": 3}}

        If inherit is used, it should be a string or a list of other
        procedures to inherit, where each item has higher priority than the
        following ones. For example:

        >>> {"inherit": "eurogoos", "sea_water_temperature": {"gradient": 2}}

        will use all the setup from eurogoos, and include/overwrite the
        gradient test for sea_water_temperature with a threshold of 2.

    Returns
    -------
    cfg : OrderedDict
        A dictionary defining a full QC procedure that defines which tests to
        run on which variables.

    See also
    --------
    utils.list_cfgs
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

    def fix_threshold(cfg):
        """Explicit threshold"""
        for t in cfg:
            if isinstance(cfg[t], (int, float)):
                cfg[t] = {"threshold": cfg[t]}
        return cfg

    def fix_regional_range(cfg):
        """Explicit regions
        """
        if "regional_range" in cfg:
            cfg["regional_range"] = {"regions": cfg["regional_range"]}
        return cfg

    def fix_profile_envelop(cfg):
        """Explicit layers

        Note
        ----
        Should I confirm that cfg['profile_envelop'] is a list?
        """
        if "profile_envelop" in cfg:
            cfg["profile_envelop"] = {"layers": cfg["profile_envelop"]}
        return cfg

    output['variables'] = OrderedDict()
    for k in keys:
        cfg[k] = fix_threshold(cfg[k])
        cfg[k] = fix_regional_range(cfg[k])
        cfg[k] = fix_profile_envelop(cfg[k])
        output['variables'][label(k)] = cfg[k]
        # output[k] = cfg[k]

    return output
