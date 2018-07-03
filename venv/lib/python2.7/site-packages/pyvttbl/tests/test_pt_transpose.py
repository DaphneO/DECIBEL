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

class Test_pt_transpose(unittest.TestCase):
    def test0(self):
        R ="""\
avg(ERROR)
COURSE   TIMEOFDAY=T1   TIMEOFDAY=T2   Total 
============================================
C1              7.167          3.222   4.800 
C2              6.500          2.889   4.333 
C3                  4          1.556   2.778 
============================================
Total           5.619          2.556   3.896 """
        
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'])        
        pt2 = pt.transpose()

        self.assertEqual(str(pt2),R)
        
    def test1(self):
        R ="""\
avg(ERROR)
TIMEOFDAY=T1,   TIMEOFDAY=T1,   TIMEOFDAY=T1,   TIMEOFDAY=T2,   TIMEOFDAY=T2,   TIMEOFDAY=T2,   Total 
  COURSE=C1       COURSE=C2       COURSE=C3       COURSE=C1       COURSE=C2       COURSE=C3           
=====================================================================================================
        7.167           6.500               4           3.222           2.889           1.556   3.896 """
        
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', rows=['TIMEOFDAY','COURSE'])        
        pt2 = pt.transpose()

        self.assertEqual(str(pt2),R)

        
    def test2(self):
        R ="""\
avg(ERROR)
TIMEOFDAY   COURSE   Value 
==========================
T1          C1       7.167 
T1          C2       6.500 
T1          C3           4 
T2          C1       3.222 
T2          C2       2.889 
T2          C3       1.556 
==========================
Total                3.896 """        
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', cols=['TIMEOFDAY','COURSE'])        
        pt2 = pt.transpose()

        self.assertEqual(str(pt2),R)
        
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_pt_transpose)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
