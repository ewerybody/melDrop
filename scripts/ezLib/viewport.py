import maya.cmds as mc

def showTriangleHudOnly(state=1):
	print( "HUDPolyCountTriangles exists: " + str(mc.headsUpDisplay( "HUDPolyCountTriangles", ex=1 )) )
	mc.evalDeferred( 'import maya.cmds as mc; mc.headsUpDisplay( "HUDPolyCountTriangles", edit=1, vis=1 )' )

def addCreatedToIsolateViewScriptJob():
	'''
	TODO: make it able to remove the scriptJob too..
	'''
	from ezLib.view import addCreatedToIsolateView
	for job in m.scriptJob(listJobs=1):
		if 'DagObjectCreated' in job and '<function addCreatedToIsolateView at ' in job:
			print('scriptJob for addCreatedToIsolateView already set up!')
			return
	m.scriptJob(e=['DagObjectCreated', addCreatedToIsolateView])