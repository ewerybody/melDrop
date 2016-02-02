
def selObjectsFromShaderWithinSelection(shader):
	from maya.cmds import ls, polyListComponentConversion, listConnections, select, sets
	from ezLib.list import uniquify
	selShapes = ls(sl=1, s=1, o=1, dag=1)
	selFaces = ls(polyListComponentConversion(tf=1), fl=1)
	selSGs = uniquify(listConnections(selShapes, type='shadingEngine'))
	inSGs  = listConnections(shader, type='shadingEngine')
	# get only SGs that are connected to the shaders in question
	# and are connected to the selected surfaces
	inSGs  = [sg for sg in inSGs if sg in selSGs]
	print 'inSGs:' + str(inSGs)
	# get remaining faces that are: connected to incoming shaders
	# and in selection
	inSGFaces = ls(polyListComponentConversion(sets(inSGs, q=1), tf=1), fl=1)
	faces = [f for f in selFaces if f in inSGFaces]
	select(faces)

def assign(surface=[],shader=[]):
	return