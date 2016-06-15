import sys
import imp
import os

Global = imp.load_source('Global', os.path.join('src', 'main', 'Global.py'))
from Global import *

Debug = imp.load_source('Debug', os.path.join(MAIN_DIR, 'utilities', 'Debug.py'))

bcolor = Debug.bcolors

def _print(msg, color = ""):
    if type(msg) != type('str'):
        print(msg)
    else:
        if NO_COLOR:
            sys.stdout.write(msg)
        else:
            sys.stdout.write(color+msg+bcolor.ENDC)
        sys.stdout.flush()

def Xprint(msg):
    _print(msg)

def Hprint(msg):
    _print(msg, bcolor.HEADER)

def Gprint(msg):
    _print(msg, bcolor.OKGREEN)

def Bprint(msg):
    _print(msg, bcolor.FAIL)

def TestEqual(expected, actual, msg):
    if expected != actual:
        Bprint('[FAIL]\n')
        Xprint(msg)
        Xprint('Expected: ')
        Xprint(expected)
        Xprint('Actual:  ')
        Xprint(actual)
        return
    Gprint('[PASS]\n')


