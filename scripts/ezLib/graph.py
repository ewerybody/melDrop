import maya.cmds as m

def createInfinityMM():
	# pmn = 'graphEditor1GraphEdanimCurveEditorMenu' # standard rmb popupmenu
	gEd = 'graphEditor1GraphEd' # graph editor name
	if not m.control( gEd, ex=1 ):
		print ('the graph editor: ' + str(gEd) + ' does not (yet) exist!! :/')
		return
	# our new popup
	pup = 'tweakGraphEditPopup'
	if not m.popupMenu( pup, ex=1 ):
		m.popupMenu( pup, parent=gEd, markingMenu=1, ctrlModifier=1 )

	m.popupMenu( pup, edit=1, deleteAllItems=1 )
	m.setParent( pup, menu=1 )

	# display infinities checkbox
	cmd = 'from maya.cmds import animCurveEditor; animCurveEditor( "' +gEd+ '", e=1, displayInfinities=int(not animCurveEditor( "' +gEd+ '", q=1, displayInfinities=1 )) )'
	m.menuItem( 'displayInfinitiesMenuItem', label='Display Infinities', checkBox=m.animCurveEditor( gEd, q=1, displayInfinities=1 ), c=cmd, radialPosition='N' )

	m.menuItem( 'preInfinityMenuItem', label='< Pre Infinity', subMenu=True, parent=pup ) # radialPosition='W'
	m.menuItem( 'postInfinityMenuItem', label='Post Infinity >', subMenu=True, parent=pup ) # , radialPosition='E'
	m.menuItem( 'bothInfinityMenuItem', label='< Both Infinity >', subMenu=True, parent=pup ) # , radialPosition='S'

	infType = ['cycle', 'linear', 'constant', 'cycleRelative', 'oscillate']
	itemList = ['preInfinityMenuItem', 'postInfinityMenuItem', 'bothInfinityMenuItem']
	for i in range(3):
		for type in infType:
			cmd = 'from maya.cmds import setInfinity;'
			if i != 0:
				cmd += 'setInfinity( poi="' + type + '" );'
			if i != 1:
				cmd += 'setInfinity( pri="' + type + '" );'
			m.menuItem( label=type, parent=itemList[i], c=cmd )