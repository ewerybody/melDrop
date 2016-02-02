'''
animation related stuff
'''
from maya.cmds import *

def matchToTransformation(objects=[], channels=['t']):
	'''
	moves transform animation curves according to the actual transformation
	'''
	from ezLib import transform
	objects = transform.get(objects)
	dim = ['x','y','z']
	time = currentTime(q=1)
	
	for o in objects:
		for c in channels:
			plug = o + '.' + c
			vCurr = getAttr(plug)[0]
			vAnim = getAttr(plug, t=time)[0]
			for i in range(3):
				keyframe(plug + dim[i], vc=(vCurr[i] - vAnim[i]), e=1, iub=1, r=1, o='over')


# this is if you do not use S for keying ALL but the shift+W/E/R keys to key one transform type at a time
# this operation unfortunately is not able to handle animating components. But this does:
def keyTranslate():
	'''
	handles keying position of components as well as transforms position
	'''
	sel = ls(sl=1)
	if not sel:
		print ('nothing'),
		return

	# transforms # do the standard 
	if ls(sel, tr=1):
		setKeyframe(at='translate')

	# components # intresting: we don't need to tell setKeyframe the shape nor
	# do we have to translate the '.cv[' to '.cp[' nor it needs the .xv .yv .zv
	# attributes nor we need to make it one by one so we can do this directly in one go:
	types = [28,31] # vertices, Nurbs CVs
	components = filterExpand(sel, selectionMask=types, expand=0)
	if components:
		setKeyframe(components)