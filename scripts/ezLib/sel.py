# selection related stuff
from maya.cmds import *
from maya.mel import eval

def invertShell():
	sel = ls(sl=1, fl=1)
	eval('polyConvertToShell')
	select(sel, deselect=1)