'''
convenience stuff related to the maya viewport
'''

import maya.cmds as mc
from maya.mel import eval as melEval
import logging
log = logging.getLogger(__name__)

def getActiveModelPanel():
    '''
    returns list with relevant modelPanels
    if there is one under cursor or focused: only that
    if none applies: all visible ones
    '''
    # first under cursor
    p = mc.getPanel(underPointer=1)
    if p and mc.getPanel(typeOf=p) == 'modelPanel':
        return [p]
    # ok then try focused
    p = mc.getPanel(withFocus=1)
    if p and mc.getPanel(typeOf=p) == 'modelPanel':
        return [p]
    # hmm ok then look which are visible at all
    mPanels = []
    for p in mc.getPanel(visiblePanels=1):
        if mc.getPanel(typeOf=p) == 'modelPanel':
                mPanels.append(p)

    #NTH: shouldn't I raise an error if there is an empty list to return?
    return mPanels

def toggleIsolate():
    '''
    singleton to toggle isolateView in current model panel
    '''
    for p in getActiveModelPanel():
        if mc.modelEditor(p, q=1, viewSelected=1):
            # if on:simply turn of works
            mc.modelEditor(p, e=1, viewSelected=0)
        else:
            # TODO: If selection is empty, you probably don't want an empty isolated view
            # if off:we need the mel proc, it collects the objs to isolate
            melEval('enableIsolateSelect("' + p + '", 1)')

def addCreatedToIsolateView():
    '''
    if the current model editor panels isolate view is
    enabled add the just created object to the view
    '''
    for p in getActiveModelPanel():
        if mc.modelEditor(p, q=1, viewSelected=1):
            mc.modelEditor(p, edit=1, addSelected=1)

def cycleWOS():
    '''
    cycles wireframe on: all > selected > none
    '''
    mPanel = getActiveModelPanel()
    dPref = mc.displayPref(q=1, wsa=1)
    # if 'wsa' or wireframeOnShaded is off goto 1: all
    if dPref == 'none' or dPref == 'reduced':
        mc.displayPref(wsa='full')
        for p in mPanel:
            mc.modelEditor(p, e=1, wos=1)
    elif dPref == 'full':
        #NTH: i don't query "all" modelPanels but in my case there is never more that 1
        if mc.modelEditor(mPanel[0], q=1, wos=1):
            for p in mPanel:
                mc.modelEditor(p, e=1, wos=0)
        else:
            mc.displayPref(wsa='none')


def toggleXray():
    for p in getActiveModelPanel():
        x = mc.modelEditor( p, q=1, xray=1 )
        mc.modelEditor( p, edit=1, xray=not x )


# block 7 seems unused so far, but it could collide! Actually we'd need to check all HUDs for the used blocks
# headsUpDisplay(listHeadsUpDisplays=1) ...
def createSelCountHUD():
    if mc.headsUpDisplay('HUDSelCount', ex=1):
        mc.headsUpDisplay('HUDSelCount', e=1, remove=1)
    mc.headsUpDisplay('HUDSelCount', section=0, block=8, label='Sel:', dataFontSize='large',command=HUDSelCountUpdate, event='SelectionChanged')

def HUDSelCountUpdate():
    s = 0
    if mc.getPanel(wf=1) == 'graphEditor1':
        s = mc.keyframe(q=1, keyframeCount=1)
    if s:
        return s
    return len(mc.ls(sl=1, fl=1))

def toggleGrid():
    panel = mc.getPanel(withFocus=True)
    ptype = mc.getPanel(typeOf=panel)
    # if in UV Editor toggle the according grid there
    if ptype == 'scriptedPanel' and panel.startswith('polyTexturePlacementPanel'):
        state = mc.textureWindow(panel, q=True, tgl=True)
        mc.textureWindow(panel, e=True, tgl=not state)
    # else use these 2 grid toggelling methods to switch it for sure
    elif ptype == 'modelPanel':
        state = True
        if mc.grid(q=True, toggle=True) or mc.modelEditor(panel, q=True, grid=True):
            state = False
        mc.grid(toggle=state)
        mc.modelEditor(panel, e=True, grid=state)
