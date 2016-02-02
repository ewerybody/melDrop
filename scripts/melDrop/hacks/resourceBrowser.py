"""
This class creates and manages the resource browser
hacked from C:\Program Files\Autodesk\Maya2014\Python\Lib\site-packages\maya\app\general\resourceBrowser.py


"""
from maya.utils import loadStringResourcesForModule
loadStringResourcesForModule('maya.app.general.resourceBrowser')

from maya import cmds
from maya import stringTable
import os.path
from functools import partial


class resourceBrowser:
    def __init__(self):
        self.winName = "resourcesBrowser"
        self.verbose = False
        self.currentResource = None
        self.resources = cmds.resourceManager(nameFilter='*')
        self.numIconCol = 20
        self.numIconRow = 5
        self.numIcons = self.numIconCol * self.numIconRow
        self.symbolButtons = []
        self.iconsOffset = 0
    
    def setCurrent_textList(self):
        selIndx = cmds.textScrollList(self.wList, query=True, selectIndexedItem=True)
        if (selIndx is None) or (len(selIndx) < 1):
            self.currentResource = None
        self.currentResource = self.resList[selIndx[0] - 1]
        self.updatePreview()
    
    def setCurrent_iconList(self, name, *args):
        if not name:
            self.currentResource = None
        else:
            self.currentResource = name
        self.updatePreview()
    
    def updatePreview(self):
        selected = True
        if self.currentResource is None:
            self.currentResource = "commandButton.png"
            selected = False
        
        cmds.iconTextStaticLabel(self.wItemImage, edit=True,
                                 image=self.currentResource, enable=selected)
    
    def updateFilter(self, data):
        """
        Update the list based on the new filter
        """
        self.iconsOffset = 0
        if not data:
            self.resList = list(self.resources)
        else:
            self.resList = [e for e in self.resources if data in e.lower()]
        
        cmds.textScrollList(self.wList, edit=True, removeAll=True)
        for name in self.resList:
            cmds.textScrollList(self.wList, edit=True, append=name)
        cmds.textScrollList(self.wList, edit=True, selectIndexedItem=1)
        
        self.updateIconList()
        cmds.setFocus(self.wList)
        self.updatePreview()
    
    def updateIconList(self):
        for i, sb in enumerate(self.symbolButtons):
            if i >= len(self.resList[self.iconsOffset:self.numIcons + self.iconsOffset]):
                cmds.symbolButton(sb, edit=True, image='', command='',
                                  annotation='', visible=False)
            else:
                r = self.resList[self.iconsOffset:self.numIcons + self.iconsOffset][i]
                cmds.symbolButton(sb, edit=True, image=r, annotation=r, visible=True,
                                  command=partial(self.setCurrent_iconList, r))
    
    def saveCopy(self, data):
        "Button callback to end the dialog"

        resName = self.currentResource
        if resName is None:
            return

        ext = os.path.splitext(resName)[1]
        if ext == '':
            ext = '.png'

        # Bring a file browser to select where to save the copy
        captionStr = stringTable['y_resourceBrowser.kPickIconCaption']
        iconDir = cmds.internalVar(userBitmapsDir=True)
        fileList = cmds.fileDialog2(caption=captionStr,
                                    fileMode=0,
                                    okCaption=captionStr,
                                    fileFilter='*' + ext,
                                    startingDirectory=iconDir)
        path = None
        if fileList is not None:
            if len(fileList) > 0 and fileList[0] != "":
                path = fileList[0]

        if path is not None:
            cmds.resourceManager(saveAs=(resName, path))
    
    def buttonCallback(self, data, dismissMsg=''):
        "Button callback to end the dialog"
        cmds.layoutDialog(dismiss=dismissMsg)

    def populateUI(self):
        "Create the resource browser window UI"

        # Get the dialog's formLayout.
        form = cmds.setParent(q=True)

        col = cmds.columnLayout(adj=True)
        self.wFilter = cmds.textFieldGrp(label=stringTable['y_resourceBrowser.kFilter'],
                                         columnAttach=[(1, "right", 5), (2, "both", 0)],
                                         columnWidth=(1, 75),
                                         adjustableColumn=2,
                                         text='',
                                         textChangedCommand=self.updateFilter)
        self.checkRow = cmds.rowLayout(nc=5)
        cmds.checkBox(label='x', cc=self._switchList)
        cmds.checkBox(label='only icon format (32px)')
        cmds.checkBox(label='png')
        cmds.checkBox(label='svg')
        cmds.checkBox(label='match case')
        cmds.setParent('..')
        self.wList = cmds.textScrollList(numberOfRows=11, visible=False,
                                         allowMultiSelection=False,
                                         selectCommand=self.setCurrent_textList)
        
        self.iFrame = cmds.frameLayout(labelVisible=False, marginHeight=6, marginWidth=6)
        cmds.rowLayout(nc=2, rowAttach=[2, 'both', -2], adjustableColumn=1)
        self.iList = cmds.rowColumnLayout(numberOfColumns=self.numIconCol)
        for _i in range(100):
            sb = cmds.symbolButton(h=32, w=32)
            self.symbolButtons.append(sb)
        cmds.setParent('..')
        upDownForm = cmds.formLayout(w=40)
        bUp = cmds.button(label='^', w=40, h=35, c=partial(self._upDownOffset, -40))
        bDn = cmds.button(label='v', w=40, h=35, c=partial(self._upDownOffset, 40))
        cmds.setParent('..')
        cmds.formLayout(upDownForm, edit=True,
                        attachForm=[(bUp, 'top', 1),
                                    (bDn, 'bottom', 1)])
        cmds.setParent('..')
        cmds.setParent('..')
        
        self.wItemImage = cmds.iconTextStaticLabel(image="commandButton.png")
        cmds.setParent('..')
        
        b1 = cmds.button(label=stringTable['y_resourceBrowser.kSelect'],
                         command=partial(self.buttonCallback, dismissMsg="valid"))
        b2 = cmds.button(label=stringTable['y_resourceBrowser.kSaveCopy'],
                         annotation=stringTable['y_resourceBrowser.kSaveCopyAnn'],
                         command=self.saveCopy)
        b3 = cmds.button(label=stringTable['y_resourceBrowser.kCancel'],
                         command=self.buttonCallback)

        cmds.formLayout(form, edit=True,
                        attachForm=[(col, 'top', 6),
                                    (col, 'left', 6),
                                    (col, 'right', 6),

                                    (b1, 'left', 6),
                                    (b1, 'bottom', 6),
                                    (b2, 'bottom', 6),
                                    (b3, 'right', 6),
                                    (b3, 'bottom', 6)],

                        attachPosition=[(b1, 'right', 3, 33),
                                        (b2, 'right', 3, 66)],
                        
                        attachControl=[(b2, 'left', 6, b1),
                                       (b3, 'left', 6, b2)]
                        )

        self.updateFilter('')

    def _upDownOffset(self, amount, *args):
        #self.iconsOffset = min(max(0, self.iconsOffset + amount), len(self.resList))
        self.iconsOffset = min(max(0, self.iconsOffset + amount), len(self.resList) - self.numIcons)
        self.updateIconList()

    def _switchList(self, state):
        cmds.textScrollList(self.wList, edit=True, visible=state)
        cmds.frameLayout(self.iFrame, edit=True, visible=not state)

    def run(self):
        """Display the Factory Icon Browser window. Return the selected
        resource or None
        """

        result = cmds.layoutDialog(title=stringTable['y_resourceBrowser.kShelves'],
                                   ui=self.populateUI)

        if result == 'valid':
            return self.currentResource
        return None


# Copyright (C) 1997-2013 Autodesk, Inc., and/or its licensors.
# All rights reserved.
#
# The coded instructions, statements, computer programs, and/or related
# material (collectively the "Data") in these files contain unpublished
# information proprietary to Autodesk, Inc. ("Autodesk") and/or its licensors,
# which is protected by U.S. and Canadian federal copyright law and by
# international treaties.
#
# The Data is provided for use exclusively by You. You have the right to use,
# modify, and incorporate this Data into other products for purposes authorized
# by the Autodesk software license agreement, without fee.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND. AUTODESK
# DOES NOT MAKE AND HEREBY DISCLAIMS ANY EXPRESS OR IMPLIED WARRANTIES
# INCLUDING, BUT NOT LIMITED TO, THE WARRANTIES OF NON-INFRINGEMENT,
# MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE, OR ARISING FROM A COURSE
# OF DEALING, USAGE, OR TRADE PRACTICE. IN NO EVENT WILL AUTODESK AND/OR ITS
# LICENSORS BE LIABLE FOR ANY LOST REVENUES, DATA, OR PROFITS, OR SPECIAL,
# DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES, EVEN IF AUTODESK AND/OR ITS
# LICENSORS HAS BEEN ADVISED OF THE POSSIBILITY OR PROBABILITY OF SUCH DAMAGES.
