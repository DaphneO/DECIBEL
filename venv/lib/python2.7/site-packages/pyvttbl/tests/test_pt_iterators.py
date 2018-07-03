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

class Test_pt_mathmethods__iter__(unittest.TestCase):

    def test1(self):
        
        R =["""\
avg(ERROR)
TIMEOFDAY   COURSE=C1   COURSE=C2   COURSE=C3 
=============================================
T1              7.167       6.500           4 """,
"""\
avg(ERROR)
TIMEOFDAY   COURSE=C1   COURSE=C2   COURSE=C3 
=============================================
T2              3.222       2.889       1.556 """]
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'])

        for r,L in zip(R, pt):
            self.assertAlmostEqual(r, str(L))
            
    def test2(self):
        
        R =np.array([[ 7.16666667],
                     [ 6.5],
                     [ 4.],
                     [ 3.22222222],
                     [ 2.88888889],
                     [ 1.55555556]])
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', rows=['TIMEOFDAY','COURSE'])

        self.assertEqual(str(R.shape),str(pt.shape))

        for r,L in zip(R.flatten(),pt.flatten()):
            self.assertAlmostEqual(r,L)
            
    def test3(self):
        
        R =np.array([[7.16666667,
                      6.5,
                      4.,
                      3.22222222,
                      2.88888889,
                      1.55555556]])
         
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', cols=['TIMEOFDAY','COURSE'])

        self.assertEqual(str(R.shape),str(pt.shape))

        for r,L in zip(R.flatten(),pt.flatten()):
            self.assertAlmostEqual(r,L)
            

    def test4(self):
        
        R =["""\
avg(ERROR)
TIMEOFDAY                       COURSE=C1                                           COURSE=C2                                         COURSE=C3                   
=================================================================================================================================================================
T1          [10.0, 8.0, 6.0, 8.0, 7.0, 4.0, None, None, None]   [9.0, 10.0, 6.0, 4.0, 7.0, 3.0, None, None, None]   [7.0, 6.0, 3.0, 4.0, 5.0, 2.0, 3.0, 4.0, 2.0] """,
"""\
avg(ERROR)
TIMEOFDAY                     COURSE=C1                                       COURSE=C2                                       COURSE=C3                   
=========================================================================================================================================================
T2          [5.0, 4.0, 3.0, 4.0, 3.0, 3.0, 4.0, 1.0, 2.0]   [4.0, 3.0, 3.0, 4.0, 2.0, 2.0, 3.0, 3.0, 2.0]   [2.0, 2.0, 1.0, 2.0, 3.0, 2.0, 1.0, 0.0, 1.0] """]
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'],aggregate='tolist')

        for r,L in zip(R,pt):
            self.assertEqual(r, str(L))

    def test5(self):
        
        R =["""\
avg(ERROR)
COURSE   TIMEOFDAY=T1   TIMEOFDAY=T2 
====================================
C1              7.167          3.222 ""","""\
avg(ERROR)
COURSE   TIMEOFDAY=T1   TIMEOFDAY=T2 
====================================
C2              6.500          2.889 ""","""\
avg(ERROR)
COURSE   TIMEOFDAY=T1   TIMEOFDAY=T2 
====================================
C3                  4          1.556 """]
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'])

        for r,L in zip(R, pt.transpose()):
            self.assertAlmostEqual(r, str(L))
            
class Test_pt_mathmethods_flat(unittest.TestCase):

    def test1(self):
        
        R =[7.16666666667, 6.5, 4.0,
            3.22222222222, 2.88888888889, 1.55555555556]
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'])

        for r,L in zip(R,pt.flat):
            self.assertEqual('%.5f'%r, '%.5f'%L)

    def test2(self):
        
        R =[7.16666666667, 6.5, 4.0,
            3.22222222222, 2.88888888889, 1.55555555556]
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY','COURSE'])

        for r,L in zip(R,pt.flat):
            self.assertEqual('%.5f'%r, '%.5f'%L)
            
    def test3(self):

        R =[7.16666666667, 6.5, 4.0,
            3.22222222222, 2.88888888889, 1.55555555556]
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', cols=['TIMEOFDAY','COURSE'])

        for r,L in zip(R,pt.flat):
            self.assertEqual('%.5f'%r, '%.5f'%L)
            
class Test_pt_mathmethods_ndenumerate(unittest.TestCase):

    def test1(self):
        
        R =[7.16666666667, 6.5, 4.0,
            3.22222222222, 2.88888888889, 1.55555555556]

        Rinds = [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2)]
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY'],['COURSE'])

        i=0
        for inds,L in pt.ndenumerate():
            self.assertEqual('%.5f'%L, '%.5f'%R[i])
            self.assertEqual(str(inds), str(Rinds[i]))
            i+=1  

    def test2(self):
        
        R =[7.16666666667, 6.5, 4.0,
            3.22222222222, 2.88888888889, 1.55555555556]

        Rinds = [(0,0),(1,0),(2,0),(3,0),(4,0),(5,0)]
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', ['TIMEOFDAY','COURSE'])

        i=0
        for inds,L in pt.ndenumerate():
            self.assertEqual('%.5f'%L, '%.5f'%R[i])
            self.assertEqual(str(inds), str(Rinds[i]))
            i+=1
            
    def test3(self):

        R =[7.16666666667, 6.5, 4.0,
            3.22222222222, 2.88888888889, 1.55555555556]

        Rinds = [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5)]
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        pt = df.pivot('ERROR', cols=['TIMEOFDAY','COURSE'])

        i=0
        for inds,L in pt.ndenumerate():
            self.assertEqual('%.5f'%L, '%.5f'%R[i])
            self.assertEqual(str(inds), str(Rinds[i]))
            i+=1                

def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_pt_mathmethods__iter__),
            unittest.makeSuite(Test_pt_mathmethods_flat),
            unittest.makeSuite(Test_pt_mathmethods_ndenumerate)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
