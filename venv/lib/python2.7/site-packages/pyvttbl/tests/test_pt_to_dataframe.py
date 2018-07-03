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
import math

import numpy as np

from pyvttbl import DataFrame
from pyvttbl.misc.support import *

class Test_pyvttbl_to_dataframe(unittest.TestCase):
    def test0(self):
        R = """\
TIME    CONDITION=A   CONDITION=B 
=================================
day           1.864         1.933 
night         1.622         1.731 """
        
        df = DataFrame()
        df.read_tbl('data/example.csv')
        df['LOG10_X']=[math.log10(x) for x in df['X']]
        pt = df.pivot('LOG10_X', ['TIME'], ['CONDITION'])
        df2 = pt.to_dataframe()
        
        self.assertEqual(str(df2),R)

    def test1(self):
        R = """\
CYCLE   PHASE   GROUP=AA,   GROUP=AA,   GROUP=AB,   GROUP=AB,   GROUP=LAB,   GROUP=LAB, 
                 AGE=old    AGE=young    AGE=old    AGE=young    AGE=old     AGE=young  
=======================================================================================
    1   I          17.750       8.675      12.625       5.525       21.625        7.825 
    1   II         20.875       8.300      22.750       8.675       36.250       13.750 
    2   I          22.375      10.225      23.500       8.825       21.375        9.900 
    2   II         28.125      10.250      41.125      13.100       46.875       14.375 
    3   I          23.125      10.500      20.000       9.125       23.750        9.500 
    3   II         20.750       9.525      46.125      14.475       50.375       15.575 
    4   I          20.250       9.925      15.625       7.750       26.375        9.650 
    4   II         24.250      11.100      51.750      12.850       46.500       14.425 """
        df = DataFrame()
        df.read_tbl('data/suppression~subjectXgroupXageXcycleXphase.csv')
        pt = df.pivot('SUPPRESSION',
                  rows=['CYCLE', 'PHASE'],
                  cols=['GROUP', 'AGE'])
        df2 = pt.to_dataframe()

        self.assertEqual(str(df2),R)

    def test2(self):
        R = """\
GROUP=AA,   GROUP=AA,   GROUP=AB,   GROUP=AB,   GROUP=LAB,   GROUP=LAB, 
 AGE=old    AGE=young    AGE=old    AGE=young    AGE=old     AGE=young  
=======================================================================
   22.188       9.813      29.188      10.041       34.141       11.875 """
        df = DataFrame()
        df.read_tbl('data/suppression~subjectXgroupXageXcycleXphase.csv')
        pt = df.pivot('SUPPRESSION',
                  cols=['GROUP', 'AGE'])
        df2 = pt.to_dataframe()
       
        self.assertEqual(str(df2),R)

    def test3(self):
        R = """\
GROUP    AGE    Value  
======================
AA      old     22.188 
AA      young    9.813 
AB      old     29.188 
AB      young   10.041 
LAB     old     34.141 
LAB     young   11.875 """
        df = DataFrame()
        df.read_tbl('data/suppression~subjectXgroupXageXcycleXphase.csv')
        pt = df.pivot('SUPPRESSION',
                  rows=['GROUP', 'AGE'])
        df2 = pt.to_dataframe()

        self.assertEqual(str(df2),R)
        
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_pyvttbl_to_dataframe)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
