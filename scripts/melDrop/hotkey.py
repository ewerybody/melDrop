import maya.cmds as mc
#from maya.mel import eval as melEval
#import json
import logging
log = logging.getLogger(__name__)
from os.path import dirname
import os
import prefs

longKeys = ['Up', 'Down', 'Left', 'Right', 'Page_Up', 'Page_Down', 'Home',
            'End', 'Insert', 'Return', 'Space', 'F1', 'F2', 'F3', 'F4',
            'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']

mwTweaksFile = os.path.join(dirname(__file__), 'mayaWrangler.json')
# idea: hold the hotkey tweaks right here and load them up on init
# so mayaWrangler.hotkeys.tweaks is already the dict with all the hotkey presets
tweaks = None
debug = True


def setup(name, config, *args):
    """
    Applies the given data to a hotkey. Anything that will be overwritten is saved in
    the melDrop prefs file: melDrop.json located in your Maya versions pref folder
    """
    alt = 'alt' in config
    ctl = 'ctl' in config
    
    # remember current settings if there are any.
    # gather returns empty dict if not but we save that anyway to just delete
    # the hotkey when its deactivated
    current = gather(config['key'], ctl, alt)
    
    fromLabel = ''
    if current:
        fromLabel = ' (from: %s)' % current['name']
    
    prefsDict = prefs.getPrefs()
    if 'hotkeyBackups' not in prefsDict:
        prefsDict['hotkeyBackups'] = {}
    
    label = makeKeyLabel(config)
    prefsDict['hotkeyBackups'][label] = current
    prefs.setPrefs(prefsDict)
    setHotkey(name, config)
    log.info('set: (%s) %s%s' % (label, name, fromLabel))


def setHotkey(name, config, *args):
    log.info('setHotkey: name: %s' % name)
    if 'nameCommand' in config and config['nameCommand'] != "":
        nameCmd = config['nameCommand']
    else:
        nameCmd = name + '_NameCommand'
    # if there is no special category set make it 'User'
    if 'cat' in config and config['cat'] != "":
        cat = config['cat']
    else:
        cat = 'User'
    # if there is no doc text/annotation just give it the name for now
    if 'text' in config and config['text'] != "":
        text = config['text']
    else:
        text = name
    # create runtimeCommand, which is wisible in Hotkey Editor and contains actual code!
    runTimeCmd = createRunTimeCommand(name, config['code'], text, cat, config.get('lang'))
    # create a nameCommand which is triggered by the hotkey
    nameCmd = mc.nameCommand(nameCmd, ann=text, c=runTimeCmd, sourceType=config['lang'])
    # now the actual hotkey with the keys and modifiers
    mc.hotkey(k=config['key'], name=nameCmd, alt='alt' in config, ctl='ctl' in config)


def reset(name, config, keyLabel, *args):
    """
    I wish I could actually delete a hotkey completely! But there is no way!
    I can not even hack the userHotkeys.mel and userNamedCommands.mel prefs file!
    Because they might be overwritten anytime.
    """
    prefsDict = prefs.getPrefs()
    if keyLabel not in prefsDict['hotkeyBackups']:
        log.error('keyLabel "%s" could not be found to restore')
        return
    backup = prefsDict['hotkeyBackups'][keyLabel]
    if not backup:
        mc.hotkey(k=config['key'], name="", alt='alt' in config, ctl='ctl' in config)
        log.info('removed: (%s)' % keyLabel)
    else:
        setHotkey(backup['name'], backup)
        log.info('restored: (%s) %s ' % (keyLabel, backup['name']))
    
    if mc.runTimeCommand(name, ex=True) and not mc.runTimeCommand(name, q=True, default=True):
        mc.runTimeCommand(name, e=True, delete=True)

    prefsDict['hotkeyBackups'].pop(keyLabel)
    prefs.setPrefs(prefsDict)


def createRunTimeCommand(name, code, ann='', cat='User', lang='python'):
    """
    runTimeCommands are all the entries listed in the Hotkey Editor.
    They can be called directly but they can't be fired by a hotkey. For that
    you need another nameCommand that the hotkey points to...
    DAMN: although it seems to work like any other func runTimeCommand does NOT
    return the name of the created thing!!
    """
    
    edit = mc.runTimeCommand(name, ex=True)
    # default commands can't be overwritten
    if edit and mc.runTimeCommand(name, q=True, default=True):
        return name

    #code = code.replace('\n','\\n')
    #code = code.replace('"','\\"')
    
    mc.runTimeCommand(name, edit=edit, ann=ann, cat=cat, c=code, commandLanguage=lang)
    #if edit:
    #    edit = '-edit'
    #else:
    #    edit = ''
    #cmd = 'runTimeCommand %s -ann "%s" -cat "%s" -c "%s" -commandLanguage "%s" "%s";' % (edit, ann, cat, code, lang, name)
    #print('cmd: ' + str(cmd))
    #melEval(cmd)
    return name


def gather(key, ctl=0, alt=0):
    '''
    returns dict {name, key, code, ann, cat, alt, ctl}
    '''
    if len(key) > 1:
        key = key.title()
    nCmd = getNameCommand(key, ctl, alt)
    if not nCmd:
        return {}
    rtCmd = getRunTimeCommand(nCmd)
    if not rtCmd:
        log.error('nameCommand found: "%s" but no runTimeCommand! "%s"' % (nCmd, rtCmd))
        return {}
    try:
        code = mc.runTimeCommand(rtCmd, q=True, command=True)
        ann = mc.runTimeCommand(rtCmd, q=True, annotation=True)
        cat = mc.runTimeCommand(rtCmd, q=True, category=True)
        lang = mc.runTimeCommand(rtCmd, q=True, commandLanguage=True)
    except:
        log.error('could not query runTimeCommand for "%s"' % rtCmd)
        return {}
    
    data = {'name': rtCmd, 'key': key, 'code': code, 'text': ann,
            'cat': cat, 'lang': lang, 'nameCommand': nCmd}
    if alt:
        data['alt'] = True
    if ctl:
        data['ctl'] = True
    return data


def makeKeyLabel(hkDict):
    """
    From a hotkey data dict assembles display friendly version for UI and simple
    one string comparison.
    
    For instance makes:
    Alt+Shift+G out of: 'alt': True, 'key': 'G'
    """
    keys = []
    if 'ctl' in hkDict:
        keys.append('Ctrl')
    if 'alt' in hkDict:
        keys.append('Alt')
    if len(hkDict['key']) == 1 and hkDict['key'].isupper():
        keys.append('Shift')
    keys.append(hkDict['key'].title())
    return '+'.join(keys)


def getNameCommand(key, ctl=0, alt=0):
    """
    From a key-string plus ctl(bool) and alt(bool) get the internal 'nameCommand'
    that holds the very script code for a hotkey.
    """
    if not isinstance(key, basestring):
        log.error('getNameCommand needs key given as string!')
        return ''
    if len(key) > 1:
        key = key.title()
    # Whow! This is severe! Feeding "hotkey" without such a check kills Maya instantly
    if len(key) == 1 or key in longKeys:
        return mc.hotkey(key, query=True, alt=alt, ctl=ctl, name=True)
    else:
        log.error('Key invalid: "%s"' % key)
        return ''


def getRunTimeCommand(nameCmd):
    """
    As there is no way to get a runtimeCommand from a nameCommand directly. This
    browses all 'assignedCommands' for the given nameCommand until it matches
    """
    for i in range(1, mc.assignCommand(q=True, num=True) + 1):
        if mc.assignCommand(i, q=True, name=True) == nameCmd:
            return mc.assignCommand(i, q=True, command=True)
    return ''
