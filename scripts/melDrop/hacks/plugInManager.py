'''
Finally a Plug-In Manager that doesn't suck.
Created on 25.06.2015

TODO: pluginInfo -changedCommand "updatePluginCallback();";
TODO: do uiRes shit
@author: eric
'''
from maya import cmds
import os
from _functools import partial
name = 'PlugInManager'
from melDrop.ui import formArrange


class PlugInManager(object):
    def __init__(self):
        self.paths = []
        
        if cmds.window(name, ex=True):
            cmds.deleteUI(name)
        self.win = cmds.window(name)
        self.formLyt = cmds.formLayout()
        self.scroLyt = cmds.tabLayout(childResizable=True, scrollable=True,
                                      tabsVisible=False)
        self.columnL = cmds.columnLayout(adjustableColumn=True)
        cmds.setParent(self.formLyt)
        cmds.button(label='Browse')
        cmds.button(label='Refresh')
        cmds.button(label='Close', c=self.close)
        formArrange(self.formLyt, ['bottom >', 'top, right 33%',
                                   'top, left 33%, right 66%', 'top, left 66%'], 1)
        
        self.getPlugInPaths()
        self.buildWidgets()
        
        cmds.showWindow(self.win)

    def close(self, *args):
        cmds.evalDeferred(partial(cmds.deleteUI, self.win))

    def buildWidgets(self):
        cmds.setParent(self.columnL)
        for path in self.paths:
            # gather actual plugin files # if( `about -mac` ) '.bundle' '.so'
            plugins = []
            for f in os.listdir(path):
                for x in ['.mll', '.py', '.pyc', '.nll.dll']:
                    if f.lower().endswith(x):
                        plugins.append(f)
                        break
            # TODO: remove .pyc that are available as .py as well
            plugins.sort()
            
            
            # TODO: handle collapsing via cmds.optionVar(q="PluginManagerState")
            collapsed = False
            label = '%s - %i' % (path, len(plugins))
            cmds.frameLayout(marginHeight=10, marginWidth=10, labelVisible=True,
                             borderStyle="etchedIn", borderVisible=True,
                             collapse=collapsed, collapsable=True, label=label,
                             collapseCommand=partial(self.handleCollape, path),
                             expandCommand=partial(self.handleCollape, path))
            
            cmds.columnLayout(adjustableColumn=True)
            cbLabels = ['Loaded','Auto Load']
            
            if len(plugins) > 1:
                allCb = cmds.checkBoxGrp(numberOfCheckBoxes=2, label='Apply To All',
                                         cal=[1,"left"], la2=cbLabels)
                cmds.separator(h=10, style='in')
            
            for p in plugins:
                cmds.checkBoxGrp(numberOfCheckBoxes=2, label=p,
                                     cal=[1,"left"], la2=cbLabels)
            
            cmds.setParent('..')
            cmds.setParent('..')
    
    def handleCollape(self, name, *args):
        print('handleCollape: %s' % name)
    
    def getPlugInPaths(self):
        sep = ';' if cmds.about(nt=True) else ':'
        paths = os.getenv('MAYA_PLUG_IN_PATH').split(sep)
        paths = [p.replace('\\', '/') for p in paths if os.path.exists(p)]
        self.paths = list(set(paths))
        