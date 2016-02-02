'''
polygon mesh related stuff
'''
import maya.mel

def pointOnPolyHelper(maintainoffset=1):
	'''
	utilites the built in maya command but maintains offset and
	adds a nearesPointOnSurface node to get hold of the correct UV values
	'''
	from ezLib.list import uniquify
	from maya.cmds import *
	sel = ls(sl=1)
	shape = uniquify(ls(ls(sel, s=1, o=1, dag=1), type='mesh'))
	shapeTrans = uniquify(listRelatives(shape, parent=1))
	if len(shapeTrans) > 1:
		raise IOError, 'multiple mesh transforms! Select the shape that you want to attach to directly!'
	shapeTrans = shapeTrans[0]

	# check for underworld shapes
	nonIntermediates = []
	if len(shape) > 1:
		for s in shape:
			if not getAttr(s + '.intermediateObject'):
				nonIntermediates.append(s)
	if len(nonIntermediates) > 1:
		raise IOError, 'multiple visible mesh shapes selected! Select the shape that you want to attach to directly!'
	shape = nonIntermediates[0]

	tr = ls(sel, tr=1)
	if tr.count(shapeTrans):
		tr.remove(shapeTrans)

	npom = createNode('nearestPointOnMesh')
	connectAttr(shape + '.worldMesh[0]', npom + '.inMesh')
	for t in tr:
		tpos = xform(t, q=1, t=1)
		trot = xform(t, q=1, ro=1)
		setAttr(npom + '.inPosition', tpos[0], tpos[1], tpos[2])
		nuv = [getAttr(npom + '.parameterU'), getAttr(npom + '.parameterV')]
		# selection order is important!
		select(shape, t)
		maya.mel.eval('performPointOnPolyConstraint 0;')
		# get new constraint
		popc = listRelatives(t, type='constraint')[0]
		setAttr(popc + '.' + shapeTrans + 'U0', nuv[0])
		setAttr(popc + '.' + shapeTrans + 'V0', nuv[1])
		if maintainoffset:
			npos = getAttr(npom + '.position')[0]
			setAttr(popc + '.offsetTranslate', tpos[0] - npos[0], tpos[1] - npos[1], tpos[2] - npos[2])

	delete(npom)
	select(sel)


# bind to the 2 nearest joints only:
# TODO: make foolproof
def skinBindUpToNearesJoint(debug=0):
	from maya.cmds import *
	import ezLib.util
	reload(ezLib.util)
	if debug: # timing
		from time import time
		t1 = time()

	# get objects and skinCluster
	vtxs = ls(polyListComponentConversion(tv=1), fl=1)
	js   = ls(sl=1, type='joint')
	if not js or len(js) < 2:
		raise IOError, 'Need at least 2 joints!'
	sc = listConnections(js[0], type='skinCluster')[0]

	# get joint positions
	jps = []
	jn = len(js)
	for j in js:
		jps.append(xform(j, q=1, t=1, ws=1))

	# browse each vertex
	for v in vtxs:
		vp = pointPosition(v)
		# collect 2 nearest joints
		jds = [[js[0], ezLib.util.dist(vp,jps[0])], ['',None]]
		for i in range(1,jn):
			d = ezLib.util.dist(vp,jps[i])
			# check collection from bottom
			if d < jds[0][1]:
				jds[1] = jds[0] # shift to 2nd
				jds[0] = [js[i], d] # new value becomes 1st
			elif jds[1][1] == None or d < jds[1][1]:
				jds[1] = [js[i], d] # new value becomes 1st

		a = jds[0][1] / (jds[0][1] + jds[1][1])
		# print (v + ' gets these values: ' + str(a) + ' & ' + str(-a + 1))
		skinPercent(sc, v, transformValue=[(jds[1][0], a), (jds[0][0], -a + 1)])
	if debug:
		print('time taken: ' + str(time() - t1))


def jointify(name=''):
	from maya.cmds import *
	# get mesh transforms
	import ezLib.transform
	mTrfs = ezLib.transform.get(shape='mesh')
	if not mTrfs:
		raise IOError, 'No mesh shapes found!'

	if not name:
		p = mTrfs[0].split('|')[1]
		if p[0:14] == 'cryExportNode_':
			name = p.split('_')[1]
		else:
			name = 'jointify'

	js = []
	counts = []
	for mt in mTrfs:
		sn = mt.split('|')[-1]
		# create joints at transform positions
		pos = xform(mt, q=1, t=1, ws=1)
		j = createNode('joint', n=(sn + 'joint'))
		xform(j, t=pos)
		js.append(j)
		
		# plug each channel driver into the appropriate joint
		for t in 'trs':
			for d in 'xyz':
				input = listConnections((mt + '.' + t + d), p=1)
				if input:
					connectAttr(input[0], (j + '.' + t + d))
		# collect nr of verts - this method collects also children if any
		counts.append(len(ls(polyListComponentConversion(mt, tv=1), fl=1)))

	dupMesh = duplicate(mTrfs, renameChildren=1)
	dupMesh = polyUnite(dupMesh, ch=0)

	# check for multiple UVsets
	uvSets = polyUVSet(dupMesh, q=1, allUVSets=1)
	for i in range(1,len(uvSets)):
		# for each set other than the 1st: set it, copy to 1st, delete it
		polyUVSet(dupMesh, currentUVSet=1, uvSet=uvSets[i])
		polyCopyUV(dupMesh[0] + '.map[*]', uvSetNameInput=uvSets[i], uvSetName=uvSets[0])
		polyUVSet(dupMesh, uvSet=uvSets[i], delete=1)
	# cleanup history crap
	delete(dupMesh, ch=1)

	sc = skinCluster(js, dupMesh)[0]
	vtxNr = 0
	for i in range(len(js)):
		vtxSel = dupMesh[0] + '.vtx[' + str(vtxNr) + ':' + str(vtxNr + counts[i] - 1) + ']'
		skinPercent(sc, vtxSel, transformValue=[js[i], 1])
		vtxNr += counts[i]

	root = createNode('joint', n=name + 'rootjoint')
	setAttr(root + '.drawStyle', 2)
	parent(js, root)
	select(root, dupMesh)


def removeExtraUVSets():
	from maya.cmds import polyUVSet, polyCopyUV
	import ezLib.transform
	mts = ezLib.transform.get(shape='mesh')
	for m in mts:
		uvSets = polyUVSet(m, q=1, allUVSets=1)
		for i in range(1,len(uvSets)):
			# for each set other than the 1st: set it, copy to 1st, delete it
			polyUVSet(m, currentUVSet=1, uvSet=uvSets[i])
			polyCopyUV(m + '.map[*]', uvSetNameInput=uvSets[i], uvSetName=uvSets[0])
			polyUVSet(m, uvSet=uvSets[i], delete=1)
			
# copy vertexColorsWithoutTransferNode
#obj = ls(sl=1, tr=1)
#vtxs = ls(obj[0] + '.vtx[*]', fl=1)
#for v in vtxs:
#    vtx = '.' + v.split('.')[1]
#    rgb = polyColorPerVertex(obj[0] + vtx, q=1, rgb=1) 
#    a = polyColorPerVertex(obj[0] + vtx, q=1, a=1)[0]
#    polyColorPerVertex(obj[1] + vtx, a=a, rgb=rgb)