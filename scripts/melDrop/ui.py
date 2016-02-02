from maya import cmds
import logging
from os.path import dirname
import os
import json
import hotkey
from functools import partial
from prefs import getPrefs

name = 'melDrop'

logging.basicConfig()
log = logging.getLogger(name)


class MelDropUI(object):
    def __init__(self):
        self.prefsDict = getPrefs()
        self.buildUi()
        self.root = dirname(dirname(dirname(__file__)))
        self.refresh()
    
    def buildUi(self):
        self.ui = {}
        self.ui['labelW'] = 70
        if cmds.window(name, ex=True):
            cmds.deleteUI(name)
        self.ui['win'] = cmds.window(name, title=name)
        self.ui['winLayout'] = cmds.formLayout()
        
        self.ui['butonBar'] = cmds.rowLayout(numberOfColumns=2)
        cmds.button(label='refresh list', c=self.refresh)
        cmds.button(label='reload mod', c=reloadMe)
        cmds.button(label='reload mod', c=reloadMe)
        cmds.setParent('..')
        
        self.ui['tabLayout'] = cmds.tabLayout(selectCommand=self.update, scrollable=True, childResizable=True)
        self.ui['myTweaks'] = cmds.columnLayout(adjustableColumn=True)
        cmds.tabLayout(self.ui['tabLayout'], edit=True,
                       tabLabel=((self.ui['myTweaks'], 'myTweaks')))
        
        cmds.showWindow(self.ui['win'])
        formArrange(self.ui['winLayout'], [[['bottom']], [['top', self.ui['butonBar']]]], 0)
    
    def update(self):
        pass
    
    def refresh(self, *args):
        self.tweaks = self.getTweaks()
        self.drawTweakTabs()
        self.drawMyTweaks()

    def drawMyTweaks(self):
        cmds.setParent(self.ui['myTweaks'])
        log.debug(self.prefsDict)
        
        for d in self.prefsDict:
            if d == 'hotkeyBackups':
                continue
            cmds.button(label='tweak: %s' % d)

        cmds.button(label='create tweak')
        
    def drawTweakTabs(self):
        mainTl = self.ui['tabLayout']
        tabs = cmds.tabLayout(mainTl, q=True, childArray=True)
        labels = cmds.tabLayout(mainTl, q=True, tabLabel=True)
        for twkLst in self.tweaks:
            # search tabs for this tweak list
            try:
                idx = labels.index(twkLst)
                # delete content if layout is available
                col = tabs[idx]
                content = cmds.columnLayout(col, q=True, childArray=True)
                if content:
                    cmds.deleteUI(content)
            # or create a new one
            except:
                col = cmds.columnLayout(adjustableColumn=True, parent=mainTl)
                cmds.tabLayout(mainTl, edit=True, tabLabel=((col, twkLst)))

            for typ in self.tweaks[twkLst]:
                if not self.tweaks[twkLst][typ]:
                    continue
                for item in self.tweaks[twkLst][typ]:
                    if typ == 'hotkeys':
                        keyLabel = hotkey.makeKeyLabel(self.tweaks[twkLst][typ][item])
                        checkValue = 'hotkeyBackups' in self.prefsDict and keyLabel in self.prefsDict['hotkeyBackups']
                        
                        # a collapsable frame with checkbox in front
                        cmds.rowLayout(numberOfColumns=2, parent=col, adjustableColumn=2)
                        cmds.checkBox(label='', w=20, value=checkValue,
                                      onCommand=partial(hotkey.setup, item, self.tweaks[twkLst]['hotkeys'][item]),
                                      offCommand=partial(hotkey.reset, item, self.tweaks[twkLst]['hotkeys'][item], keyLabel))
                        cmds.frameLayout(label=('%s (%s)') % (item, keyLabel), collapsable=True, collapse=True, borderStyle='in')
                        
                        cmds.columnLayout(adjustableColumn=True)
                        # first version: write everything in textFields:
                        for attr in self.tweaks[twkLst][typ][item]:
                            cmds.textFieldGrp(label='%s:' % attr, text=self.tweaks[twkLst][typ][item][attr],
                                              cw=(1, self.ui['labelW']), adjustableColumn=2)

                        key = self.tweaks[twkLst][typ][item]['key']
                        ctl = 'ctl' in self.tweaks[twkLst][typ][item]
                        alt = 'alt' in self.tweaks[twkLst][typ][item]
                        data = hotkey.gather(key, ctl, alt)
                        # show the override item when any hotkey is already found
                        if data:
                            # and if set by us and actually overrides something
                            if checkValue:
                                if self.prefsDict['hotkeyBackups'][keyLabel]:
                                    overrideLabel = self.prefsDict['hotkeyBackups'][keyLabel]['name']
                                else:
                                    overrideLabel = None
                            else:
                                overrideLabel = data['name']
                            if overrideLabel:
                                cmds.textFieldGrp(label='overrides:', text=overrideLabel, bgc=(0.4, 0, 0),
                                                  cw=(1, self.ui['labelW']), adjustableColumn=2)
    
    # TODO:
    #def drawHotkeyUI(self, item, editable=False, override=False):
    #    if 'text'
    #    if 'text' in item:
    #        mc.textFieldGrp( label='name:', text=item['name'], bgc=(0.4,0,0), cw=(1, self.ui['labelW']), adjustableColumn=2, editable=editable )
    
    def getTweaks(self):
        jsons = [j for j in os.listdir(self.root) if os.path.isfile(os.path.join(self.root, j)) and j.endswith('.json')]
        tweaks = {}
        for j in jsons:
            with open(os.path.join(self.root, j), 'r') as jsonFileObj:
                jtweaks = json.load(jsonFileObj)
                tweaks[os.path.splitext(j)[0]] = jtweaks
        return tweaks


def show():
    return MelDropUI()


def reloadMe(*args):
    import sys
    import inspect
    import traceback
    melDropMods = [m for m in sys.modules if m.startswith('melDrop') and inspect.ismodule(sys.modules[m])]
    if melDropMods:
        log.info('reloading modules: %s' % ','.join(melDropMods))
        for m in melDropMods:
            try:
                log.info(m)
                reload(sys.modules[m])
            except RuntimeError, e:
                tb = traceback.format_exc().strip()
                raise RuntimeError(e, tb)
        log.info('reload comlete!')
    show()


def formArrange(form, arrangements, offset=3, ca=None):
    '''
    Easy formLayout arranging.
    The idea is to attach to each side by default.
    So you only state exceptions!

    In order of control creation add layout statements for each control for each
    side you want to do something with:
    ['side controlName/arrows/percentage%/offset offset, ...']
    
    Example for a complete arrangement statement for a control:
        [ 'left, right 50%, top 10, bottom checkbox1 5', ... ]

        don't attach to the left,
        attach to right at 50%,
        attach to top with a 10px offset and
        attach to bottom at control 'checkbox1' with 5px offset

    In detail:
        FIRST part is always a side:
            left, right, top or bottom.
            If a side is omitted it's attached by the default offset.
            If a side is stated without anything it's not attached to this side.
        If LAST part is a single number it's describing an offset.
            If a side is just stated with an offset it's attached by this.
        SECOND part can be a control name, a pointer to the next '>' or previous
            control '<' in the formLayoyts control list
            (also: '>>' next but one ...) or a percentage indication
    
    This might all be too much of a mouthful. Just to make sure: This is
    actually made to make things easier! So here an example for a standard use
    case: A flexible top control and fixed one at the bottom:
    
    ------------------
    |----------------|
    ||       ^      ||
    ||       |      ||
    ||       v      ||
    |----------------|
    |----------------|
    ||              ||
    |----------------|
    ------------------
    
    Where there are those 2 control layouts within the formLayout 'form':

        formArrange(form, ['bottom >','top'] )
        
    Voila! That's all!
    
    In former versions of formArrange this was all stated by lists within lists:
    [ ['left'],['right','50%'],['top',10],['bottom','checkbox1',5] ]
    '''
    # get ca "childArray"
    if not ca:
        ca = cmds.formLayout(form, q=True, ca=True)
    if ca is None:
        raise IOError('formArrange: nothing to arrange')

    attachNone = []
    attachForm = []
    attachPosition = []
    attachControl = []

    i = 0
    # browse all statements
    for arr in arrangements:
        # convert string if not in list layout
        if not isinstance(arr, list) and isinstance(arr, basestring):
            arr = [a.strip().split(' ') for a in arr.split(',')]
            # make trailing digits int
            for a in arr:
                if len(a) > 1 and (isinstance(a[-1], basestring) and a[-1].isdigit()):
                    a[-1] = int(a[-1])
        
        control = ca[i]
        # browse each direction
        # if command is found add it or make direction do attachForm
        for d in ['left', 'right', 'top', 'bottom']:
            try:
            # look where in this arr this side is defined
                dx = [a[0] for a in arr].index(d)
            except:
            # not definded: default make this side attachForm
                attachForm.append((control, d, offset))
                continue
            # statement for this side is only 1 long: means do not attach
            if len(arr[dx]) == 1:
                attachNone.append((control, d))
                continue
            # last part of the direction part is an int: change offset:
            thisOffset = offset
            if isinstance(arr[dx][-1], int):
                thisOffset = arr[dx][-1]
                # if this is true and there are only 2 parts its another offset:
                if len(arr[dx]) == 2:
                    attachForm.append((control, d, thisOffset))
                    continue
            # use attachPosition if 2nd part of statement is a percentage sign
            if arr[dx][1][-1] == '%':
                attachPosition.append((control, d, thisOffset,
                                       int(arr[dx][1][0:-1])))
                continue
            # use attachControl if the 2nd part is a string name of another
            # control or < or >> for previous or next but one, so you don't need
            # to extra state the name of the control
            if isinstance(arr[dx][1], basestring):
                to = arr[dx][1]
                if to.count('<'):
                    to = ca[i - to.count('<')]
                elif to.count('>'):
                    to = ca[i + to.count('>')]
                attachControl.append((control, d, thisOffset, to))
        # statement loop, increase count
        i += 1
    #     text = ('cmds.formLayout(form, edit=True, af=%s, an=%s, ap=%s, ac=%s)'
    #             % (attachForm, attachNone, attachPosition, attachControl))
    #     print('text: %s' % text)
    cmds.formLayout(form, edit=True, af=attachForm, an=attachNone,
                    ap=attachPosition, ac=attachControl)
