import maya.cmds as m
currTimeField = 'floatField1' # apparently the currentTimeField is the first floatField created
lyout = 'formLayout9' # in Maya 2012 the layout is formLayout9: fka "formLayout46"


def createSecondsCurrentTimeField():
	# add an extra currentTime field that displays seconds instead of frames
	fieldName = 'secondsCurrentTimeField'
	if m.control( fieldName, ex=1 ):
		print ('extra currentTime field exists: ' + str(fieldName) + '. deleting...')
		m.deleteUI( fieldName )

	# fps - todo: add all cases
	fps = 25
	if m.currentUnit(q=1, t=1) == 'ntsc':
		fps = 30

	scds = m.currentTime( q=1 ) / fps
	cmd  = 'from maya.cmds import currentTime, floatField; currentTime( floatField( "' + fieldName + '", q=1, v=1 ) * ' + str(fps) + ')'
	# make the field change the currentTime on scrubb
	m.floatField( fieldName, w=60, pre=2, value=scds, parent=lyout,  cc=cmd )
	m.formLayout( lyout, e=1,  attachControl=[(currTimeField, 'right', 1, fieldName), (fieldName, 'right', 1, 'gridLayout1')],  attachForm=[(fieldName, 'top', 5)] )
	# make currentTime changes adjust the new field
	cmd  = 'from maya.cmds import currentTime, floatField; floatField( "' + fieldName + '", e=1, value=currentTime( q=1 ) / ' + str(fps) + ' )'
	m.scriptJob( parent=fieldName,  event=["timeChanged", cmd] )


# make the field work with whole frames instead of 0.01s of frames
def makeCurrentTimeFieldInt():
	print ('editing standard time field: ' + str(currTimeField) + ' to work with int...')
	m.floatField( currTimeField, e=1, pre=0, step=1 )


# a popup on the right float fields to make the currentTime the maximum range
def addCurrentTimeToMinMaxPopup():
	print( 'adding range editing popup on currentTime field...' )
	popUps = m.floatField( currTimeField, q=1, popupMenuArray=1 )
	if popUps:
		m.deleteUI( popUps )
	m.popupMenu( 'currentTimeToMinMaxPopup', p=currTimeField, mm=1, button=3, pmc=currentTimeToMinMaxPopup )

def currentTimeToMinMaxPopup(*args):
	m.popupMenu( 'currentTimeToMinMaxPopup', edit=True, deleteAllItems=True )
	m.setParent( 'currentTimeToMinMaxPopup', menu=True )
	curTime = m.currentTime(q=1)
	curMin = m.playbackOptions( q=1, min=1 )
	curMax = m.playbackOptions( q=1, max=1 )
	if curTime != curMin and curTime != curMax:
		m.menuItem( rp='W',  label='currentTime to range Min', command=lambda bla1,c=curTime: m.playbackOptions(min=c) )
		m.menuItem( rp='E',  label='currentTime to range Max', command=lambda bla2,c=curTime: m.playbackOptions(max=c) )
	else:
		m.menuItem( label='currentTime is min or max already', en=False )
	# set to range of current objs
	if m.keyframe( q=1, keyframeCount=1 ) == 0:
		m.menuItem( label='no keyframes in selection', en=False )
		return
	frst = m.findKeyframe( which='first' )
	last = m.findKeyframe( which='last' )
	if frst == last:
		return
	
	txt = 'set range to selected %i - %i'%(frst,last)
	m.menuItem( rp='N',  label=txt, command=lambda bla,mn=frst,mx=last: m.playbackOptions(e=1, min=mn, max=mx) )