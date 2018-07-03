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

class Test_pt_mathmethods__add__(unittest.TestCase):
    def test0(self):
        # __add__ constant
        R ="""\
N/A(ERROR)
TIMEOFDAY   COURSE=C1   COURSE=C2   COURSE=C3   Total  
======================================================
T1             12.167      11.500           9   10.619 
T2              8.222       7.889       6.556    7.556 
======================================================
Total           9.800       9.333       7.778    8.896 """
        
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'])
##        print(pt)
        pt2=pt+5
        
        self.assertEqual(str(pt2),R)

    def test1(self):
        # __add__ PyvtTbl
        R ="""\
N/A(ERROR)
TIMEOFDAY   COURSE=C1   COURSE=C2   COURSE=C3   Total  
======================================================
T1             14.333          13           8   11.238 
T2              6.444       5.778       3.111    5.111 
======================================================
Total           9.600       8.667       5.556    7.792 """
        
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'])
        pt2=pt+pt
        
        self.assertEqual(str(pt2),R)
        
    def test2(self):
        # __add__ ndarray
        R ="""\
N/A(ERROR)
TIMEOFDAY   COURSE=C1   COURSE=C2   COURSE=C3 
=============================================
T1             12.167      11.500           9 
T2              8.222       7.889       6.556 """
                
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'])
        pt2=pt+np.array([[5,5,5], [5,5,5]])
        
        self.assertEqual(str(pt2),R)
        

class Test_pt_mathmethods__mul__(unittest.TestCase):
    def test0(self):
        # __mul__ constant
        R ="""\
N/A(ERROR)
TIMEOFDAY   COURSE=C1   COURSE=C2   COURSE=C3   Total  
======================================================
T1             35.833      32.500          20   28.095 
T2             16.111      14.444       7.778   12.778 
======================================================
Total              24      21.667      13.889   19.479 """
        
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'])
        pt2=pt*5

##        print(pt2)
        
        self.assertEqual(str(pt2),R)

    def test1(self):
        R ="""\
N/A(ERROR)
TIMEOFDAY   COURSE=C1   COURSE=C2   COURSE=C3   Total  
======================================================
T1             51.361      42.250          16   31.574 
T2             10.383       8.346       2.420    6.531 
======================================================
Total          23.040      18.778       7.716   15.178 """
        
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        sums = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'],aggregate='sum')
        counts = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'],aggregate='count')
        aves = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'],aggregate='avg')
        calc_aves = sums/counts.astype(np.float64)
        
##        print('\n'.join(str(aves).split('\n')[1:]))
##        print('\n'.join(str(calc_aves).split('\n')[1:]))
        
        self.assertEqual('\n'.join(str(aves).split('\n')[1:]),
                         '\n'.join(str(calc_aves).split('\n')[1:]))
        
    def test2(self):
        # __mul__ ndarray
        R ="""\
N/A(ERROR)
TIMEOFDAY   COURSE=C1   COURSE=C2   COURSE=C3 
=============================================
T1             35.833      32.500          20 
T2             16.111      14.444       7.778 """
                
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'])
        pt2=pt*np.array([[5,5,5], [5,5,5]])

##        print(pt2)
        
        self.assertEqual(str(pt2),R)

     
class Test_pt_mathmethods_sum(unittest.TestCase):
    def test0(self):
        # __add__ constant
        R ="""\
N/A(ERROR)
TIMEOFDAY   COURSE=C1   COURSE=C2   COURSE=C3   Total  
======================================================
T1             12.167      11.500           9   10.619 
T2              8.222       7.889       6.556    7.556 
======================================================
Total           9.800       9.333       7.778    8.896 """
        
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'])
        self.assertAlmostEqual(np.sum(pt),25.3333333333, 5)

        
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_pt_mathmethods__add__),
            unittest.makeSuite(Test_pt_mathmethods__mul__),
            unittest.makeSuite(Test_pt_mathmethods_sum)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
