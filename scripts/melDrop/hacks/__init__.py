'''
melDrop.hacks

Created 2014
@author: eric
'''


def betterIconBrowser():
    """
    monkey patches the Maya-shipped factory icon browser
    with one thats faster, has a find-when-typing search bar,
    shows a nice array of icons with preview at the bottom that
    doesn't shift around the ui.
    TODO: implement the filters
        * 32x32 * svg * png
    
    TODO: enable unloading:
    import maya.app.general.resourceBrowser
    reload(maya.app.general.resourceBrowser)
    """
    import maya.app.general.resourceBrowser
    import resourceBrowser
    maya.app.general.resourceBrowser.resourceBrowser = resourceBrowser.resourceBrowser


def betterSriptEdCompletions():
    """
    monkey patches the Maya-shipped autocompletion function in the Script
    Editor to avoid duplicates and show public (non _funcs) first
    
    TODO: enable unloading:
    import maya.utils
    reload(maya.utils)
    """
    import maya.utils
    from maya2014 import getPossibleCompletions
    maya.utils.getPossibleCompletions = getPossibleCompletions
