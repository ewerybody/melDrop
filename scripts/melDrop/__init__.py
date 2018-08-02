"""
meldrop init
"""
import os
import sys
import json
import logging
import importlib

from maya import mel
from maya import cmds

import prefs


log = logging.getLogger('meldrop_init')


def start():
    """
    Looks up and runs the registered tweaks that need to be initiated at Maya
    start. Usually UI tweaks or overrides to the Maya built-in stuff.

    These are either Mel or Python things. Both are sourced/imported,
    catched and checked for successful start.
    """
    prefs_dict = prefs.load()
    if not prefs_dict:
        log.info('nothing to start up! Well, cheers!\n')
        return

    log.info('hello!')
    for tweak in prefs_dict.get('tweaks', []):
        if tweak.get('enabled': False):
            try:
                log.info('starting: %s ...' % tweak['name'])
                tweak_module = importlib.import_module('meldrop.tweaks.' + tweak['name'])
                tweak_module.start(tweak.get('options'))
            except AttributeError or KeyError:
                pass
