import maya.cmds as m


def isEmpty():
    '''
    pseudo secure test if the scene is an empty one.
    '''
    thisScene = m.ls()
    # if node count is different from defaults this can't be an empty scene
    nodeCount = len(thisScene)
    if nodeCount not in [64, 65]:
        print('not isEmptyScene because: nodeCount: ' + str(nodeCount))
        return False
    # if it fits check for node names
    dfltScene = 'time1 sequenceManager1 renderPartition renderGlobalsList1 '\
                'defaultLightList1 defaultShaderList1 postProcessList1 '\
                'defaultRenderUtilityList1 defaultRenderingList1 lightList1 '\
                'defaultTextureList1 lambert1 particleCloud1 initialShadingGroup '\
                'initialParticleSE initialMaterialInfo shaderGlow1 dof1 '\
                'defaultRenderGlobals defaultRenderQuality defaultResolution '\
                'defaultLightSet defaultObjectSet defaultViewColorManager '\
                'hardwareRenderGlobals hardwareRenderingGlobals characterPartition '\
                'defaultHardwareRenderGlobals ikSystem hyperGraphInfo '\
                'hyperGraphLayout globalCacheControl dynController1 persp '\
                'perspShape top topShape front frontShape side sideShape '\
                'lightLinker1 brush1 strokeGlobals layersFilter objectTypeFilter74 '\
                'animLayersFilter objectTypeFilter75 notAnimLayersFilter '\
                'objectTypeFilter76 defaultRenderLayerFilter objectNameFilter4 '\
                'renderLayerFilter objectTypeFilter77 objectScriptFilter10 '\
                'renderingSetsFilter objectTypeFilter78 '\
                'relationshipPanel1LeftAttrFilter relationshipPanel1RightAttrFilter '\
                'layerManager defaultLayer renderLayerManager defaultRenderLayer '\
                'CustomGPUCacheFilter objectTypeFilter79'.split()
    
    # different names identify a changed scene
    diff = [obj for obj in thisScene if obj not in dfltScene]
    if diff:
        print('not isEmptyScene because of this node: ' + str(diff))
        return False
    return True


def addOrderCamsFirstOnSceneLoadScriptJob():
    for job in m.scriptJob(listJobs=1):
        if 'SceneOpened' in job and '<function orderCamsFirst at ' in job:
            print('scriptJob for orderCamsFirst already set up!')
            return
    m.scriptJob(e=['SceneOpened', orderCamsFirst])


def orderCamsFirst():
    '''
    makes sure the default cameras are first in scene hierarchy
    '''
    assemblies = m.ls(assemblies=True, long=True)
    if assemblies[0] != "|persp":
        for cam in ["|side", "|front", "|top", "|persp"]:
            m.reorder(cam, front=True)


def group(objs=None):
    '''
    groups the selected objects but keeps the position in hierarchy and selection alive
    '''
    objs = getObjs(objs, tr=True)
    n = getOrder(objs[0])
    g = m.group()
    setOrder(g, n)
    m.select(m.listRelatives(g, children=True, type='transform'))
    m.evalDeferred("import maya.cmds as m;m.outlinerEditor('outlinerPanel1', edit=True, showSelected=True)")


def ungroup(objs=None, selParents=False):
    '''
    contrary to maya built-in ungroup this works on the selected objs and puts them
    right next to the parent
    '''
    objs = getObjs(objs, tr=True)
    parentDict = getParents(objs)
    handled = []
    #if parentDict.has_key('0world'):   parentDict.pop('a')
    for p in parentDict:
        if p != '0world':
            handled += orderNextTo(parentDict[p], p)
    if selParents:
        m.select(parentDict.keys())
    else:
        m.select(handled)


def sort(objs=None):
    '''
    sorts a range of selected objects and
    keeps the general position in hierarchy
    '''
    objs = getObjs(objs, tr=True)
    prnts = getParents(objs)
    for p in prnts:
        if p == '0world':
            allChildren = m.ls(assemblies=True, l=True)
        else:
            allChildren = m.listRelatives(p, c=True, type='transform', f=True)
        selOfParent = {}
        for o in objs:
            selOfParent[o] = allChildren.index(o)
        sortKeys = sorted(selOfParent.keys())
        sortVals = sorted(selOfParent.values())
        for i in range(len(sortVals)):
            #transform.setOrder(allChildren[sortVals[i]], selOfParent[sortKeys[i]])
            setOrder(sortKeys[i], sortVals[i])


def getOrder(obj):
    '''
    retrieves the hierarchical position in the outliner to to make tools that avoid reordering to the bottom of the list
    example:
    dup = dulicate(obj)
    nr = getOrder(obj)
    setOrder(dup, nr)
    '''
    # from maya.cmds import ls, listRelatives
    parent = m.listRelatives(obj, p=True, f=True)
    shortName = obj.split('|')[-1]

    siblings = []
    if parent:
        siblings = m.listRelatives(parent, fullPath=True, c=True, type=['transform', 'shape'])
    else:
        siblings = m.ls(l=True, assemblies=True)

    pos = 0
    for s in siblings:
        if s.split('|')[-1] == shortName:
            return pos
        pos += 1


def setOrder(obj, nr):
    '''
    just to have this inline to use in conjunction with the getOrder function
    '''
    m.reorder(obj, front=True)
    m.reorder(obj, relative=nr)


def orderNextTo(objects, target):
    '''
    places 'objects'/[objects] next to 'target' in hierarchy and ordering

    I found most of the time I use the get/setOrder stuff to relocate objs to another
    with parenting and if in world and hierarchy Nr and all that shit.. this does it inline
    '''
    if not isinstance(objects, list):
        objects = [objects]
    handledObjs = []
    targetParent = m.listRelatives(target, parent=True, fullPath=True)
    targetNr = getOrder(target)
    # handle each object on its own no matter how its parented
    for o in objects:
        oParent = m.listRelatives(o, parent=1, fullPath=1)
        if oParent != targetParent:
            if targetParent:
                o = m.parent(o, targetParent)[0]
            else:
                o = m.parent(o, world=1)[0]
        # else if in same hierarchy already decrease count if obj is before target
        elif getOrder(o) <= targetNr:
            targetNr -= 1
        handledObjs.append(o)
    setOrder(handledObjs, targetNr + 1)
    m.select(handledObjs)
    return handledObjs


def uniquify(lst, idfun=None):
    '''
    removes duplicate items from a list
    '''
    if idfun is None:
        def idfun(x):
            return x
    seen = {}
    result = []
    for item in lst:
        marker = idfun(item)
        if marker in seen:
            continue
        seen[marker] = 1
        result.append(item)
    return result


def getObjs(objs=None, tr=False):
    if not objs:
        objs = m.ls(sl=True, tr=tr, long=True)
        if not objs:
            raise IOError('no objects given!')
    return objs


def getParents(objs=None):
    objs = getObjs(objs, tr=True)
    prnts = {}
    for o in objs:
        p = m.listRelatives(o, p=True, fullPath=True)
        # put objs without a parent in 0world, safe name: Maya obj cannot start with a number
        if not p:
            appendDict(prnts, '0world', p)
        else:
            appendDict(prnts, p[0], o)
    return prnts


def appendDict(dictionary, dictKey, dictValue):
    if dictKey not in dictionary:
        dictionary[dictKey] = []
    dictionary[dictKey].append(dictValue)
