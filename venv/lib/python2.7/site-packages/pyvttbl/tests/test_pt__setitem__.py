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

from pyvttbl import DataFrame
from pyvttbl.misc.support import *

class Test_pt__setitem__(unittest.TestCase):
    def test0(self):
        R = """\
avg(ERROR)
TIMEOFDAY   COURSE=C1   COURSE=C2   COURSE=C3   Total 
=====================================================
T1              7.167       6.500           4   5.619 
T2                  0       2.889       1.556   2.556 
=====================================================
Total           4.800       4.333       2.778   3.896 """
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'])

        pt[1,0]=0.

        self.assertEqual(R, str(pt))

    def test1(self):
        
        R ="""\
avg(ERROR)
TIMEOFDAY   COURSE=C1   COURSE=C2   COURSE=C3   Total 
=====================================================
T1                  0           0           0   5.619 
T2              3.222       2.889       1.556   2.556 
=====================================================
Total           4.800       4.333       2.778   3.896 """
        
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'])

        pt[0]=[0,0,0]
        
        self.assertEqual(R, str(pt))
        
    def test2(self):
        
        R ="""\
avg(ERROR)
TIMEOFDAY   COURSE=C1   COURSE=C2   COURSE=C3   Total 
=====================================================
T1                 --          --          --   5.619 
T2              3.222       2.889       1.556   2.556 
=====================================================
Total           4.800       4.333       2.778   3.896 """
        
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'])

        pt[0,:] = [0,0,0]
        pt.mask[0,:] = [True, True, True]

        self.assertEqual(R, str(pt))
                
    def test5(self):
        
        R ="""\
avg(ERROR)
TIMEOFDAY   COURSE=C1   COURSE=C2   COURSE=C3   Total 
=====================================================
T1                  0       6.500           4   5.619 
T2                  0       2.889       1.556   2.556 
=====================================================
Total           4.800       4.333       2.778   3.896 """
        
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'])

        pt[:,0] = [0,0]

        self.assertEqual(R, str(pt))
        
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_pt__setitem__)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
