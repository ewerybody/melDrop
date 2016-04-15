"""
melDrop init
"""
from maya import mel
from maya import cmds as mc
import os
import sys
import json
from ui import show
import prefs


import logging
log = logging.getLogger(__name__)


# make changes to the viewport context menus
# the built-in mel scripts offer ways to alter these through
# ...UserMM.mel files,
# this helps to set up the files and make changes
# usd = mc.internalVar(userScriptDir=True)
# userMMs = [f for f in os.listdir(usd) if f.endswith('UserMM.mel')
#    and f.startswith('context') and os.path.isfile(os.path.join(usd, f))]


def start():
    """
    Looks up and runs the registered tweaks that need to be initiated at Maya
    start. Usually UI tweaks or overrides to the Maya built-in stuff.

    These are either Mel or Python things. Both are sourced/imported,
    catched and checked for successful start.
    """
    if not mc.optionVar(ex='melDropStartUp'):
        log.info('nothing to start up! Well, cheers!\n')
        return
    # fetches THIS Maya melDrop-prefs
    prefsDict = prefs.getPrefs()


def builtInScripts(method=1):
    if method == 1:
        mayaDir = os.path.sep.join(sys.executable.split(os.path.sep)[:-2])
    elif method == 2:
        import _winreg
        aKey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
                               r"SOFTWARE\\Autodesk\\Maya\\2014\\Setup\InstallPath")
        mayaDir = os.path.abspath(_winreg.QueryValueEx(aKey,
                                                       "MAYA_INSTALL_LOCATION")[0])
    return mayaDir


def aboutDict():
    ret = {}
    for l in [l.strip().split('-')[2] for l in mc.help('about').split('\n') if l.count('-')]:
        if l in ['query']:
            continue
        ret[l] = eval('mc.about(%s=True)' % l)
    return ret


"""
# C:\Program Files\Autodesk\Maya2013\scripts\others\texturePanel.mel
# textureWindowCreatePopupContextMenu
contextUVToolsUVUserMM
contextUVToolsVertexUserMM
contextUVToolsFaceUserMM
contextUVToolsEdgeUserMM
contextUVToolsObjectUserMM
contextUVToolsDefaultUserMM
# C:\Program Files\Autodesk\Maya2013\scripts\others\contextToolsMM.mel
# contextToolsMM
contextPolyToolsDefaultUserMM
# C:\Program Files\Autodesk\Maya2013\scripts\others\polyConvertMM.mel
# polyConvertMM
polyConvertUserMM
# C:\Program Files\Autodesk\Maya2013\scripts\others\contextPolyToolsMM.mel
# contextPolyToolsMM
contextPolyToolsVertexUserMM
contextPolyToolsFaceUserMM
contextPolyToolsEdgeUserMM
contextPolyToolsUVUserMM
contextPolyToolsObjectUserMM

w = mc.window()
c = mc.columnLayout()
p = mc.popupMenu(parent=c, button=1)
mc.showWindow(w)
mel.eval('contextPolyToolsMM("%s")' % p)


mc.popupMenu(p, edit=True, markingMenu=True, parent=c, button=1)
p = 'window1|columnLayout50|popupMenu155'

mc.popupMenu(p, q=True, itemArray=True)
"""
