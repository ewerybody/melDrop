from maya import cmds


def createInfinityMM():
	# pmn = 'graphEditor1GraphEdanimCurveEditorMenu' # standard rmb popupmenu
	gEd = 'graphEditor1GraphEd' # graph editor name
	if not cmds.control(gEd, ex=True):
		print('the graph editor: ' + str(gEd) + ' does not (yet) exist!! :/')
		return
	# our new popup
	pup = 'tweakGraphEditPopup'
	if not cmds.popupMenu(pup, ex=True):
		cmds.popupMenu(pup, parent=gEd, markingMenu=1, ctrlModifier=1)

	cmds.popupMenu(pup, edit=True, deleteAllItems=True)
	cmds.setParent(pup, menu=True)

	# display infinities checkbox
	cmd = ('from maya.cmds import animCurveEditor; '
		   'animCurveEditor("{gEd}", e=True, displayInfinities=int(not '
		   'animCurveEditor("{gEd}", q=True, displayInfinities=True)))'.format(gEd=gEd))
	cmds.menuItem('displayInfinitiesMenuItem', label='Display Infinities',
				  checkBox=cmds.animCurveEditor( gEd, q=1, displayInfinities=1 ),
				  c=cmd, radialPosition='N')

	cmds.menuItem('preInfinityMenuItem', label='< Pre Infinity', subMenu=True, parent=pup) # radialPosition='W'
	cmds.menuItem('postInfinityMenuItem', label='Post Infinity >', subMenu=True, parent=pup) # , radialPosition='E'
	cmds.menuItem('bothInfinityMenuItem', label='< Both Infinity >', subMenu=True, parent=pup) # , radialPosition='S'

	infType = ['cycle', 'linear', 'constant', 'cycleRelative', 'oscillate']
	itemList = ['preInfinityMenuItem', 'postInfinityMenuItem', 'bothInfinityMenuItem']
	for i in range(3):
		for type in infType:
			cmd = 'from maya.cmds import setInfinity;'
			if i != 0:
				cmd += 'setInfinity( poi="' + type + '" );'
			if i != 1:
				cmd += 'setInfinity( pri="' + type + '" );'
			cmds.menuItem(label=type, parent=itemList[i], c=cmd)
