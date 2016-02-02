'''
# shelfSwitcher popupmenu

* sort clicked ones up
'''
mmName = 'shelfSwitcherMM'
mayaShelf = 'ShelfLayout'
import maya.cmds as m

def build():
	if m.popupMenu( mmName, ex=1 ):
		m.deleteUI(mmName)
	m.popupMenu( mmName, markingMenu=True, button=3, parent='MainShelfLayout', postMenuCommand=show )

class ShelfSwitcher(object):
	def __init__(self):
		current = m.shelfTabLayout( mayaShelf, q=1, selectTab=1 )
		m.popupMenu( mmName, e=1, deleteAllItems=1 )
		showEmpty = m.optionVar( q=mmName + 'displayEmpty' )
		showSubmn = m.optionVar( q=mmName + 'showSubmn' )
		sortRecnt = m.optionVar( q=mmName + 'sortRecnt' )
		m.setParent( mmName, menu=1 )
		# create a radial menu with your favorites
		self.inRadial = []
		for pos in ['W', 'NW', 'N', 'NE', 'E', 'SE', 'S', 'SW']:
			item = m.optionVar( q=mmName + pos )
			if item:
				self.inRadial.append(item)
				label = item
				if item == current: label = '## ' + label + '##'
				m.menuItem( label=label, radialPosition=pos, c=lambda null, i=item, p=pos: self.to(null, i, p) ) #italicized=1 )
			elif showEmpty:
				m.menuItem( label='add current here', radialPosition=pos, c=lambda null, pos=pos:self.add(pos) )
		# list all the other shelves
		all = m.shelfTabLayout( mayaShelf, q=1, ca=1 )
		all = [i for i in all if i not in self.inRadial]

		if showSubmn:
			m.menuItem( label='all ...', subMenu=1 )

		self.recent = []
		if sortRecnt:
			if m.optionVar(ex=mmName + 'Recent'):
				self.recent = m.optionVar(q=mmName + 'Recent').split(',')
				for r in self.recent:
					if r in all:
						all.remove(r)
						all.insert(0,r)
		
		for item in all:
			label = item
			if item == current: label = '## ' + item + '##'
			m.menuItem( label=label, c=lambda null, i=item: self.to(null, i, None) )
		if showSubmn: m.setParent( '..', menu=1 )
		m.menuItem( divider=True )
		m.menuItem( label='settings...', subMenu=1 )
		m.menuItem( label='display empty', checkBox=showEmpty, c=lambda null, var='displayEmpty':self.checkVar(null,var) )
		m.menuItem( label='submenu', checkBox=showSubmn, c=lambda null, var='showSubmn':self.checkVar(null,var) )
		m.menuItem( label='sort by recent use', checkBox=sortRecnt, c=lambda null, var='sortRecnt':self.checkVar(null,var) )
		#maya.mel.eval('shelfTabChange();')

	def add( self, pos, *args ):
		current = m.shelfTabLayout( mayaShelf, q=1, selectTab=1 )
		m.optionVar( sv=[mmName + pos, current] )

	def checkVar( self, null, var, *args ):
		state = m.optionVar( q=mmName + var )
		m.optionVar( iv=[mmName + var, not state] )

	def to( self, null, shelf, pos, *args ):
		# delete from MM when CTRL is pressed
		if m.getModifiers() == 4 and pos:
			m.optionVar( rm=mmName + pos )
			return
		# remember recenctly pressed from non radial list
		if not shelf in self.inRadial:
			if shelf in self.recent:
				self.recent.remove(shelf)
			self.recent.append(shelf)
			m.optionVar( sv=[mmName + 'Recent', ','.join(self.recent)] )
		m.shelfTabLayout( mayaShelf, edit=1, selectTab=shelf )

def show( *args ):
	return ShelfSwitcher()









