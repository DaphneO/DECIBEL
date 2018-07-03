from __future__ import print_function

# Copyright (c) 2011, Roger Lew [see LICENSE.txt]
# This software is funded in part by NIH Grant P20 RR016454.

# Python 2 to 3 workarounds
import sys
if sys.version_info[0] == 2:
    _strobj = basestring
    _xrange = xrange
elif sys.version_info[0] == 3:
    _strobj = str
    _xrange = range

from collections import Counter
from pyvttbl.misc.support import *

def fcmp(d,r):
    """
    Compares two files, d and r, cell by cell. Float comparisons 
    are made to 4 decimal places. Extending this function could
    be a project in and of itself.
    """
    # we need to compare the files
    dh=open(d,'rb')
    rh=open(r,'rb')
    
    dlines = dh.readlines()
    rlines = rh.readlines()
    boolCounter = Counter()
    for dline, rline in zip(dlines,rlines):
        for dc,rc in zip(dline.split(','), rline.split(',')):
            if _isfloat(dc):
                if round(float(dc),4)!=round(float(rc),4):
                    boolCounter[False] += 1
                else:
                    boolCounter[True] += 1 
            else:
                pass
                if dc!=rc:
                    boolCounter[False]+= 1
                else:
                    boolCounter[True]+= 1    
    dh.close()
    rh.close()

    if all(boolCounter):
        return True
    else:
        return False
