import os
import json

from maya import cmds

CONFIG_FILENAME = 'meldrop.json'
CONFIG_FILEPATH = os.path.join(cmds.internalVar(userPrefDir=True), CONFIG_FILENAME)


def load():
    if os.path.isfile(CONFIG_FILEPATH):
        with open(CONFIG_FILEPATH) as fobj:
            prefs_dict = json.load(fobj)
    else:
        prefs_dict = {}
    return prefs_dict


def save(prefs_dict):
    with open(CONFIG_FILEPATH, 'w') as fobj:
        json.dump(prefs_dict, fobj, sort_keys=True, indent=2)
