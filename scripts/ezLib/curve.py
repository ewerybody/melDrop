'''
tools to work with simple nurbs curves
'''

def get(curves=[]):
	'''
	filters transforms from the selection or the objects you throw at it
	'''
	from maya.cmds import filterExpand
	
	# if nothing given get from the selection
	if not curves:
		curves = filterExpand(sm=9)
	# else check the given objects for transforms
	else:
		curves = filterExpand(curves, sm=9)

	if not curves:
		raise IOError, 'could not get curves!'

	return curves


def createFromTo(objs=[], divisions=4, degree=3):
	from maya.cmds import ls, attributeQuery, xform, pointPosition, curve
	from ezLib import transform
	# no objs put it: get from selection
	if not objs:
		objs = ls(sl=1)
	if len(objs) != 2:
		raise IOError, 'need 2 objs to get start & end from!'

	print ('objs: ' + str(objs))

	pos = []
	for i in range(2):
		# to get transforms/joints or anything that has translate attributes
		if attributeQuery('t', node=objs[i], exists=1):
			pos.append(xform(objs[i],q=1,t=1,ws=1))
		else:
			try:
				pos.append(pointPosition(objs[i], world=1))
			except IOError:
				print 'cannot get position from ' + objs[i]

	#vector from start to end
	posArray = transform.posRange(pos[0], pos[1], divisions + 1)
	crv = curve(p=posArray)
	# center pivot and reset pivot
	xform(crv, centerPivots=1)
	transform.resetPivot(crv)


def attachObject(crv=[],objects=[]):
	'''
	uses motionPath nodes to connect objects at the current position dynamically to a curve
	'''
	from maya.cmds import ls, addAttr, getAttr, setAttr, createNode, connectAttr, xform, delete, select
	crv = get(crv)
	crvShp = ls(crv,s=1,dag=1)[0]
	
	if not objects:
		objects = ls(sl=1,tr=1)
		if objects.count(crv[0]):
			objects.remove(crv[0])
	if not objects:
		raise IOError, 'curve: Check! But Objects? none?'

	print ('objects: ' + str(objects))
		
	# create attributes on the curveShape to control orientation
	addAttrs = ['worldUpType','frontAxis','upAxis', 'inverseFront', 'inverseUp','frontTwist','upTwist', 'sideTwist']
	numAddAttr = len(addAttrs)
	# normals usage:
	defaults = [4,0,2,1,1,0,0,0,0]
	# facing up:
	# defaults = [3,0,1,1,0]
	addTypes = ['long', 'long', 'long', 'bool', 'bool','double', 'double', 'double']
	curvePlugs = []
	for i in range(numAddAttr):
		name = 'mp' + addAttrs[i].capitalize()
		addAttr(crvShp, ln=name, at=addTypes[i])
		curvePlugs.append(crvShp + '.' + name)
		setAttr(curvePlugs[i], defaults[i], e=1, keyable=1)
		
	# create nearestPointOnCurve that we utilize to get parameter value for curve connector
	npoc = createNode('nearestPointOnCurve')
	connectAttr(crvShp + '.worldSpace[0]', npoc + '.inputCurve')
	for o in objects:
		thisPos = xform(o,q=1,t=1,ws=1)
		setAttr(npoc + '.inPosition', thisPos[0],thisPos[1],thisPos[2])
		thisParam = getAttr(npoc + '.parameter')
		# create the motionPath node that we use to position and orient along the curve
		mPath = createNode('motionPath')
		# only with fractionMode off we can use the .parameter as correct pos
		setAttr(mPath + '.fractionMode', 0)
		connectAttr(crvShp + '.worldSpace[0]', mPath + '.geometryPath')
		setAttr(mPath + '.uValue', thisParam)
		connectAttr(mPath + '.allCoordinates', o + '.translate')
		connectAttr(mPath + '.rotate', o + '.rotate')

		# connect to the oriention attributes on the curveShp
		for i in range(numAddAttr):
			connectAttr(curvePlugs[i], mPath + '.' + addAttrs[i])
	# cleanup
	delete(npoc)
	select(crv)


def ribbonize(crv=[], shader='lambert1', divLen=32, divWid=1):
	'''
	creates a basic curve driven mesh stream
	future versions shall have a twist, shift and width value
	that can be animated over lenght of the curve
	'''
	from ezLib import transform
	
	numInput = len(crv)
	crv = get(crv)
	for c in crv:
		crvShp = ls(c, s=1, dag=1)[0]
		o1 = createNode('offsetCurve')
		o2 = createNode('offsetCurve')
		connectAttr(crvShp + '.worldSpace[0]', o1 + '.inputCurve')
		connectAttr(crvShp + '.worldSpace[0]', o2 + '.inputCurve')
		# create visible attr at the curveShape to control ribbon width
		rw = 'ribbonWidth'
		if not attributeQuery(rw, node=crvShp, exists=1):
			addAttr(crvShp, ln=rw, at='float')
			setAttr(crvShp + '.' + rw, 10, keyable=1)
		connectAttr(crvShp + '.' + rw, o1 + '.distance')
		mtply = createNode('multiplyDivide')
		setAttr(mtply + '.input2X', -1)
		connectAttr(crvShp + '.' + rw, mtply + '.input1X')
		connectAttr(mtply + '.outputX', o2 + '.distance')
		# loft the 2 offsets
		loft = createNode('loft')
		connectAttr(o1 + '.outputCurve[0]', loft + '.inputCurve[0]')
		connectAttr(o2 + '.outputCurve[0]', loft + '.inputCurve[1]')
		tess = createNode('nurbsTessellate')
		connectAttr(loft + '.outputSurface', tess + '.inputSurface')

		# setup the surface creation
		setAttr(tess + '.format', 2) # 0 or 2 is useful. 0 'count' tries to create square quads
		setAttr(tess + '.polygonType', 1)
		setAttr(tess + '.chordHeightRatio', 0.9)
		setAttr(tess + '.uNumber', divWid)
		setAttr(tess + '.vNumber', divLen)
		setAttr(tess + '.uType', 3)
		setAttr(tess + '.vType', 1) # makes up the distribution: 2 is cv based, 1 is even distribution
		
		mesh = createNode('mesh')
		sets(mesh, e=1,forceElement='initialShadingGroup')
		tr = listRelatives(mesh, p=1)[0]
		xform(tr, pivots=xform(c, q=1,t=1, ws=1))
		connectAttr(tess + '.outputPolygon', mesh + '.inMesh')
		transform.resetPivot(tr)
		rename(tr, c + 'Ribbon')
		
	if not numInput:
		select(crv)


def rebuildCurveOnDemand(crv):
	v = getAttr(crv + '.CVs')
	if v < 4:
		raise IOError, 'curveRebuild: minimum 4 CVs!'
	rebuildCurve(crv, ch=0, rpo=1, rt=0, end=1, kr=1, kcp=0, kep=1, kt=0, s=(v-3), d=3, tol=1e-008)
	select(crv)
	
def curveRebuildAddScriptJob():
	import ezLib.curve
	from maya.cmds import ls, scriptJob
	from fnmatch import fnmatch
	# get curves that got a CVs attribute
	cvObjs = ls('*.CVs', o=1)
	cvObjs = ezLib.curve.get(cvObjs)
	# browse scriptjobs for aready setup curves
	jbs = scriptJob(listJobs=1)
	for j in jbs:
		if fnmatch(j, '*attributeChange*rebuildCurveOnDemand*'):
			print('ScriptJob already setup: ' + j + '! killing it')
			prts = j.split()
			n = int(prts[0].split(":")[0])
			if scriptJob(exists=n):
				scriptJob(kill=n)
	
	for c in cvObjs:
		print('building ScriptJob for: ' + c)
		scriptJob(attributeChange=[c + '.CVs', 'rebuildCurveOnDemand("' + c + '")'])