# mayaWrangler
import maya.cmds as m
currTimeField = 'floatField1' # apparently the currentTimeField is the first floatField created
lyout = 'formLayout9' # in Maya 2012 the layout is formLayout9: fka "formLayout46"

def show():
	if m.window( 'mayaWrangler', ex=True ):
		m.deleteUI( 'mayaWrangler' )
	m.window( 'mayaWrangler' )
	m.formLayout( 'mayaWranglerForm' )
	m.showWindow( 'mayaWrangler' )

def startUp():
	print( '########## mayaWrangler >>>>>>>>>>>>>>>>>>>>>>>>' )
	# todo embedd in interface:
	wantSecondsCurrentTimeField = 1
	wantCurrentTimeFieldInt = 1
	wantCurrentTimeToMinMaxPopup = 1
	wantTweakGraphEditPopup = 1
	wantShelfSwitcherMM = 1

	if not m.layout( lyout, ex=1 ):
		raise IOError, 'timeSlider layout: ' + lyout + ' does not exist (yet)! :/'
	print ('check! layout: ' + str(lyout) + ' exists!')
	if not m.control( currTimeField, ex=1 ):
		raise IOError, 'currTimeField: ' + currTimeField + ' does not exist (yet)! :/'
	print ('check! currTimeField: ' + str(currTimeField) + ' exists!')

	if wantSecondsCurrentTimeField:
		createSecondsCurrentTimeField()
	if wantCurrentTimeFieldInt:
		makeCurrentTimeFieldInt()
	if wantCurrentTimeToMinMaxPopup:
		addCurrentTimeToMinMaxPopup()
	if wantTweakGraphEditPopup:
		createTweakGraphEditPopup()
	if wantShelfSwitcherMM:
		import shelfSwitcher
		shelfSwitcher.build()
	print( '########## mayaWrangler <<<<<<<<<<<<<<<<<<<<<<<<<' )


