"""
melDrop hacks for Maya 2014
"""
import sys
import rlcompleter
print('imported....')
import logging
logging.basicConfig()
log = logging.getLogger('getPossibleCompletions')
log.setLevel(logging.DEBUG)


def getPossibleCompletions(instr):
    """
    orig: C:\Program Files\Autodesk\Maya2014\Python\Lib\site-packages\maya\utils.py
    
    hacked to sort the results, skip doubles and arrange them so the underscore ones
    come last.
    
    Utility method to handle command completion
    Returns in a list all of the possible completions that apply
    to the input string
    """
    completer = rlcompleter.Completer()
    listOfMatches = set()
    
    dot = 0
    if instr.endswith('.'):
        dot = instr.index('.')
        special = set()
        private = set()
    
    try:
        for index in xrange(sys.maxint):
            term = completer.complete(instr, index)
            if term is None:
                break
            if dot:
                if term[dot + 2] == '_':
                    special.add(term)
                elif term[dot + 1] == '_':
                    private.add(term)
                else:
                    listOfMatches.add(term)
            else:
                listOfMatches.add(term)
    except:
        pass
    
    listOfMatches = sorted(listOfMatches)
    if dot:
        listOfMatches += sorted(private) + sorted(special)
    return listOfMatches
