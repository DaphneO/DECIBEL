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
    
import unittest
import warnings
import os

import numpy as np

from pyvttbl import DataFrame,PyvtTbl
from pyvttbl.misc.support import *

from dictset import DictSet

class Test_pt__repr__(unittest.TestCase):
    def test0(self):
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'])
 
        self.assertEqual(repr(eval(repr(pt))), repr(pt))

    def test1(self):
                
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY','MODEL'],['COURSE'])
        
        self.assertEqual(repr(eval(repr(pt))), repr(pt))

    def test2(self):
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['MODEL','TIMEOFDAY'],['COURSE'],where=['SUBJECT != 1'])

        self.assertEqual(repr(eval(repr(pt))), repr(pt))
        
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_pt__repr__)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
