'''
to have everything like you left the scene this can
save and recover your tool and selection on save and load
'''
import maya.mel as mel
import maya.cmds as m
import os

# selectionToFileInfo
def stateToFileInfo():
    sel = m.ls(sl=1)
    selStr = '?'.join(sel)
    m.fileInfo('onSaveSelection',selStr)
    ctx = m.currentCtx()
    m.fileInfo('onSaveCtx',ctx)


def stateFromFileInfo():
    from fnmatch import fnmatch
    selInfo = m.fileInfo('onSaveSelection', q=1)
    if len(selInfo) != 0:
        sel = []
        for i in selInfo[0].split('?'):
            if m.objExists(i):
                sel.append(i)
        if len(sel):
            m.select(sel)

            hilite = []
            c1 = ['f[*','e[*','map[*','vtx[*','vtxFace[*']
            c2 = ['facet','edge','puv','vertex','pvf']
            for x in sel:
                if x.count('.'):
                    parts = x.split('.')
                    for i in range(5):
                        if fnmatch(parts[1],c1[i]) and parts[0] not in hilite:
                            hilite.append(parts[0])
                            mel.eval('doMenuComponentSelection("' + parts[0] + '", "' + c2[i] + '");')

    ctxInfo = m.fileInfo('onSaveCtx', q=1)
    if len(ctxInfo) != 0:
        print ('ctxInfo: ' + str(ctxInfo))
        try:
            m.setToolTo(ctxInfo[0])
        except:
            print 'could not set "' + ctxInfo[0] + '"!'


def load(filename, check=True):
    '''
    scene loading function. Loads file, adds it to recentFiles,
    checks for modifications if wanted. No bloat.
    '''
    type = "mayaBinary"
    ext = os.path.splitext( filename )[-1][1:].lower()
    if ext == 'ma':
        type = "mayaAscii"

    filename = filename.replace('\\','/')
    loadCmd = 'file -f -o "%s"; addRecentFile("%s", "%s");' % (filename, filename, type)
    print ('loadCmd: ' + str(loadCmd))
    if check:
        loadCmd = loadCmd.replace('"','\\"')
        mel.eval('saveChanges(\"' + loadCmd + '\")')
    else:
        mel.eval(loadCmd)


def loadLatestCrashMa():
    tmp = m.internalVar(userTmpDir=1)
    # get .ma files from temp:
    mas = [f for f in os.listdir(tmp) if os.path.splitext(f)[1].lower() == '.ma']
    mTime = None
    mFile = ''
    for ma in mas:
        this = os.path.getmtime(tmp + ma)
        if mTime is None or this > mTime:
            mTime = this
            mFile = ma
    load(tmp + mFile)


def showInFileBrowser():
    '''
    opens up the explorer with the current scene file selected if any
    TODO: try doing this without MEL!
    '''
    from os import path
    fn = m.file(q=1, sn=1)
    if fn != '':
        mel.eval('system ("explorer /select,\\"" + toNativePath("%s") + "\\"");' % fn)
