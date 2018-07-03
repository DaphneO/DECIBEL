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

class Test_pt__getitem__(unittest.TestCase):
    def test0(self):
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'])
    
        self.assertAlmostEqual(3.22222222222,pt[1,0],5)

    def test1(self):
        
        R ="""\
avg(ERROR)
TIMEOFDAY   COURSE=C1   COURSE=C2   COURSE=C3 
=============================================
T1              7.167       6.500           4 """
        
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'])
        
        self.assertEqual(R, str(pt[0]))
        
    def test2(self):
        
        R ="""\
avg(ERROR)
TIMEOFDAY   COURSE=C1   COURSE=C2   COURSE=C3 
=============================================
T1              7.167       6.500           4 """
        
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'])

        self.assertEqual(R, str(pt[0,:]))
                
    def test3(self):
        
        R ="""\
avg(ERROR)
TIMEOFDAY   COURSE=C1   COURSE=C2   COURSE=C3 
=============================================
T2              3.222       2.889       1.556 """
        
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'])

        self.assertEqual(R, str(pt[1]))
        
    def test4(self):
        
        R ="""\
avg(ERROR)
TIMEOFDAY   COURSE=C1   COURSE=C2   COURSE=C3 
=============================================
T2              3.222       2.889       1.556 """
        
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'])

        self.assertEqual(R, str(pt[-1:]))

    def test5(self):
        
        R ="""\
avg(ERROR)
TIMEOFDAY   COURSE=C1 
=====================
T1              7.167 
T2              3.222 """
        
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'])
        self.assertEqual(R, str(pt[:,0]))

    def test6(self):
        
        R ="""\
avg(ERROR)
TIMEOFDAY   COURSE=C1   COURSE=C2 
=================================
T1              7.167       6.500 
T2              3.222       2.889 """
        
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'])

        self.assertEqual(R, str(pt[:,:2]))
        
    def test7(self):
        
        R ="""\
avg(ERROR)
TIMEOFDAY   COURSE=C1   COURSE=C2 
=================================
T1              7.167       6.500 """
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'])

        self.assertEqual(R, str(pt[0,:2]))
        
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_pt__getitem__)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
