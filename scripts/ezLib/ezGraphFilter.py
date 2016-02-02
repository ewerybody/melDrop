# ezGraphFilter.py

def isIsolated():
	'''
	looks for an attribute entry or animCurves in object list of
	selectionConnection if so the view is considered as 'isolated'
	'''
	from maya.cmds import selectionConnection, ls
	from fnmatch import fnmatch
	displayed = selectionConnection('graphEditor1FromOutliner', q=1, object=1)
	if ls(displayed, type='animCurve'):
		return True
	for d in displayed:
		if fnmatch(d, '*.*'):
			return True
	return False

def reset():
	'''
	adds the actually selected objects to selectionConnection
	'''
	from maya.cmds import selectionConnection, ls
	selectionConnection('graphEditor1FromOutliner', e=1, clear=1)
	for s in ls(sl=1):
		selectionConnection('graphEditor1FromOutliner', e=1, object=s)

def isolate():
	'''
	clears and adds only selected curves to selectionConnection
	'''
	from maya.cmds import selectionConnection, keyframe, listConnections
	kSel = keyframe(q=1, sl=1, name=1)
	if not kSel:
		return

	selectionConnection('graphEditor1FromOutliner', e=1, clear=1)
	plugs = listConnections(kSel, p=1)
	for p in plugs:
		selectionConnection('graphEditor1FromOutliner', e=1, object=p)