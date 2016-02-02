from maya import cmds

def createJointAtPoint(radius=30):
    sel = cmds.ls(sl=1)
    hi = cmds.ls(hilite=1)[0]
    vtx = cmds.filterExpand(sm=31)
    pos = [0.0,0.0,0.0]
    for v in vtx:
        p = cmds.xform(v, q=1, t=1, ws=1)
        for i in range(3):
            pos[i] = pos[i] + p[i]
    for i in range(3):
        pos[i] = pos[i] / len(vtx)
    cmds.select(d=1)
    cmds.joint(p=pos, radius=radius)
    cmds.isolateSelect('modelPanel4',addSelected=1)
    cmds.select(hi)
    cmds.hilite(replace=1)
    cmds.selectType(ocm=1,vertex=1)
