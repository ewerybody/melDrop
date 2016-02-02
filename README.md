# melDrop - the new one!
Maya customization &amp; setup tool - WIP

----------------------
Still kind of a Maya enhancement distribution & setup thing. So I kept the name.

Main goal of melDrop: make changes to Maya really easy but keep track of what
you do! This goes for the Maya-built-in customization means:
* hotkeys * shelves * userMMs * userSetup
But also hacks to the UI and the shipped scripts.

Way better than copying over your rotten old prefs folder or delete it if a
problem occurs: You see what has actually been changed, you port it to a new
version easily, being notified if things don't work anymore and create your own
tweaks with maximum power and overview.


Its now a module!
-----------------
This way it doesn't interfere with the user scripts at all.


how it works
------------
melDrop manages the following stuff: set up hotkeys, override built-in mel
scripts, monkey patching Maya built-in python functions, load scripts on Maya start,
manage shelves, handle Maya-built-in customization means (like poly marking menus)...

All those things are assembled in so called 'tweaks'. For instance a tweak can
load a custom Mel tool and set up a hotkey to call it. So it has a 'hotkey' and
a 'script load' building block. One tweak can consist of multiple of those.
The single pieces are made to work as on and of in one go. So there is nothing
to worry about cleaning up after you messed around with melDrop.


a tweak dict example:

{
	"tweakName1": [
    	{
            "typ": "hotkey",
            "name": "AttributeEditor",
            "alt": true, 
            "cat": "User", 
            "code": "if(`isAttributeEditorRaised`) ...n}", 
            "key": "a", 
            "lang": "mel", 
            "text": ""
    	},
        {
            "typ": "hotkey",
    		"name": "selectShell",
      		"cat": "User", 
      		"code": "ezSelectShell;", 
      		"ctl": true, 
      		"key": "a", 
      		"lang": "mel", 
      		"text": ""
    	},
    	{
    	   "typ": "startup",
		   "file": "ezSelectShell.mel"
    	}
	],
	"tweakName2": [
	]
}

Such a json file comes with melDrop and when a tweak from it is enabled
it's copied to the user prefs so that the same tweaks with that name lies there
along with potential roll-back settings. If on deactivation of the tweak it is
unchanged from the original state the whole thing is removed from the user space.
So changed tweaks remain in the user space as well as self created ones.
