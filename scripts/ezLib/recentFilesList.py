import maya.cmds as m
import os
import time
import math
from maya.mel import eval as melEval
from functools import partial
maxAutoFiles = 25

class RecentFilesList(object):
    ui = {}
    name = 'recentFilesList'
    asDir = m.workspace(q=True, rootDirectory=True) + 'autosave/'
    print('asDir: ' + str(asDir))
    def __init__(self):
        if m.window(self.name, ex=True):
            m.deleteUI(self.name)
        self.ui['win'] = m.window(self.name, titleBar=False)
        self.ui['winlayout'] = m.columnLayout(cal=('left'), adj=1)
        m.popupMenu(button=3, postMenuCommand=self.delUi)
        recentFiles = m.optionVar(query="RecentFilesList")
        recentTypes = m.optionVar(query="RecentFilesTypeList")
        numFiles = len(recentFiles)
        # recent files buttons ------------------------------
        for i in range(numFiles):
            n = numFiles - i - 1
            f = recentFiles[n]
            r = recentTypes[n]
            if not os.path.exists(f):
                print('recent file: ' + str(f) + ' does not exist!?\n'),
                continue
            # cmd = 'import maya.mel; maya.mel.eval( "openRecentFile( \\"' + f + '\\", \\"' + r + '\\" )" ); recentFilesList.delUi()'
            # print ('cmd: ' + str(cmd))
            label = f + ' (' + getAgeString(None, f) + ' ago)'
            
            m.rowLayout(nc=2, adj=1)
            m.button(l=label, command=lambda x, f=f, r=r: self.load(f, r))
            thisDir = os.path.dirname(f)
            m.button(l='...', w=30)
            thisPop = m.popupMenu(button=1)
            #m.popupMenu( thisPop, e=True, postMenuCommand=lambda d=thisDir, p=thisPop:self.neighborMenu(path=d, popup=p) )
            m.popupMenu( thisPop, e=True, postMenuCommand=partial(self.neighborMenu, thisDir, thisPop) )
            #self.buildSortedPopup(thisPop, timePathTuples)
            m.setParent('..')
        # ---------------------------------------------------
        m.separator(height=20, style="in")
        
        m.rowLayout(nc=2, adj=2)
        m.button(label='Standard\nOpenScene', c=self.standardOpenScene, w=85, h=47)
        
        m.columnLayout(adj=1)
        m.button(l='load crash .ma from temp folder ...')
        self.ui['crashMAPop'] = m.popupMenu(button=1, postMenuCommand=self.crashMABuildMenu)

        # autosaves -----------------------------------------
        m.rowLayout(nc=2, adj=1)
        m.button(l='latest Autosaves ...')
        self.ui['autosavePop'] = m.popupMenu(button=1, postMenuCommand=self.autosaveBuildMenu)
        m.button(l='explore Autosaves', c='recentFilesList.explore( "' + self.asDir + '" )')
        m.setParent('..')
        m.setParent('..')
        # ----------------------------------------------------
        m.showWindow(self.ui['win'])

    def buildSortedPopup(self, popup, timePathTuples, *args):
        m.popupMenu(popup, edit=True, deleteAllItems=True)
        m.setParent(popup, menu=True)
        timePathTuples = sorted(timePathTuples)
        timePathTuples.reverse()
        for i in range(min(len(timePathTuples), maxAutoFiles)):
            label = timePathTuples[i][2] + ' (' + getAgeString(timePathTuples[i][0]) + ' ago)'
            m.menuItem(label=label, command=lambda x, f=timePathTuples[i][1]: self.load(f))

    def autosaveBuildMenu(self, *args):
        if not os.path.exists(self.asDir):
            raise IOError('Autosave dir "%s" does not exist!!' % self.asDir)
        timesPathFiles = [ (os.path.getmtime(self.asDir + f), self.asDir + f, f) for f in os.listdir(self.asDir) ]
        self.buildSortedPopup(self.ui['autosavePop'], timesPathFiles)

    def crashMABuildMenu(self, *args):
        tmp = m.internalVar(userTmpDir=True)
        # get .ma files from temp:
        mas = [ (os.path.getmtime(tmp + ma), tmp + ma, ma) for ma in os.listdir(tmp) if os.path.splitext(ma)[1].lower() == '.ma' ]
        self.buildSortedPopup(self.ui['crashMAPop'], mas)

    def neighborMenu(self, path, popup, *args):
        if not path.endswith('/'):
            path += '/'
        files = os.listdir(path)
        agePathTuples = [ (os.path.getmtime(path + f), path + f, f) for f in os.listdir(path) if os.path.splitext(f)[1].lower() in ['.ma', '.mb', '.fbx'] ]
        self.buildSortedPopup(popup, agePathTuples)

    def load(self, filePath, fileType=None, *args):
        self.delUi()
        if not fileType:
            fileType = filePath.split('.')[-1]
            if fileType.lower() == 'mb':
                fileType = 'mayaBinary'
            elif fileType.lower() == 'ma':
                fileType = 'mayaAscii'
        melEval('openRecentFile("%s","%s")' % (filePath, fileType))

    def delUi(self, *args):
        if m.window(self.ui['win'], ex=True):
            m.evalDeferred(lambda: m.deleteUI(self.ui['win']))
        m.showWindow("MayaWindow")

    def standardOpenScene(self, *args):
        self.delUi()
        m.evalDeferred(lambda: melEval('OpenScene'))



def show():
    return RecentFilesList()

def getAgeString(mtime=None, fileName=None):
    ageString = ''
    if not mtime and fileName:
        if not os.path.exists(fileName):
            return False
        mtime = os.path.getmtime(fileName)
    secAge = time.time() - mtime

    this = secAge / 86400
    for t in [(24, 'd '), (60, 'h '), (60, 'm ')]:
        rest = math.fmod(this, 1)
        this = int(this - rest)
        if this:
            ageString += str(this) + t[1]
        this = rest * t[0]

    return ageString + '%is' % this

def explore(filePath):
    cmd = 'system ("explorer \\"" + toNativePath("' + filePath + '") + "\\"");'
    # print ('cmd: ' + str(cmd))
    melEval(cmd)
