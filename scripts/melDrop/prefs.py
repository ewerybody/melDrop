import maya.cmds as mc
import json
from os.path import abspath, join, exists
cfgFile = 'melDrop.json'


def getPrefs():
    prefsFile = abspath(join(mc.internalVar(userPrefDir=True), cfgFile))
    if exists(prefsFile):
        with open(prefsFile) as prefsFileObj:
            prefsDict = json.load(prefsFileObj)
    else:
        prefsDict = {}
    return prefsDict


def setPrefs(prefsDict):
    prefsFile = abspath(join(mc.internalVar(userPrefDir=True), cfgFile))
    with open(prefsFile, 'w') as prefsFileObj:
        prefsFileObj.write(json.dumps(prefsDict, sort_keys=True, indent=2))
