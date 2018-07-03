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

class Test_sort(unittest.TestCase):
    def test0(self):
        R={'A': [-10.0, -9.0, -8.0, -7.0, -6.0, -5.0, -4.0, -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0],
           'B': [2.0, 2.0, 1.0, 1.0, 2.0, 2.0, 2.0, 1.0, 1.0, 1.0, 2.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 2.0, 1.0]}

        a=[4, 8, 1, 5, -7, -5, 9, 7, -8, -10, -1, -4, 3, 0., -2, 6, 2, -9, -3, -6]
        b=[1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2]

        df=DataFrame()
        for A,B in zip(a,b):
            df.insert({'A':A, 'B':B})

        df.sort(['A'])
        
        for d,r in zip(df['A'],R['A']):
            self.assertAlmostEqual(d,r)

        for d,r in zip(df['B'],R['B']):
            self.assertAlmostEqual(d,r)
            
    def test1(self):
        R={'A': [9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0, 0.0, -1.0, -2.0, -3.0, -4.0, -5.0, -6.0, -7.0, -8.0, -9.0, -10.0],
           'B': [1.0, 2.0, 2.0, 2.0, 2.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 1.0, 1.0, 2.0, 2.0]}

        a=[4, 8, 1, 5, -7, -5, 9, 7, -8, -10, -1, -4, 3, 0., -2, 6, 2, -9, -3, -6]
        b=[1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2]

        df=DataFrame()
        for A,B in zip(a,b):
            df.insert({'A':A, 'B':B})

        df.sort(['A desc',])

        for d,r in zip(df['A'],R['A']):
            self.assertAlmostEqual(d,r)

        for d,r in zip(df['B'],R['B']):
            self.assertAlmostEqual(d,r)

    def test2(self):
        R={'A': [-8.0, -7.0, -3.0, -2.0, -1.0, 1.0, 2.0, 3.0, 4.0, 9.0, -10.0, -9.0, -6.0, -5.0, -4.0, 0.0, 5.0, 6.0, 7.0, 8.0],
           'B': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0]}

        a=[4, 8, 1, 5, -7, -5, 9, 7, -8, -10, -1, -4, 3, 0., -2, 6, 2, -9, -3, -6]
        b=[1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2]

        df=DataFrame()
        for A,B in zip(a,b):
            df.insert({'A':A, 'B':B})

        df.sort(['B','A'])

        for d,r in zip(df['A'],R['A']):
            self.assertAlmostEqual(d,r)

        for d,r in zip(df['B'],R['B']):
            self.assertAlmostEqual(d,r)

    def test3(self):
        df=DataFrame()
  
        with self.assertRaises(Exception) as cm:
            df.sort()

        self.assertEqual(str(cm.exception),
                         'Table must have data to sort data')

    def test4(self):
        df=DataFrame()
        df['a']=[2]
        df['b']=[2,3]
  
        with self.assertRaises(Exception) as cm:
            df.sort()

        self.assertEqual(str(cm.exception),
                         'columns have unequal lengths')

    def test5(self):
        df=DataFrame()
        df['a']=[2,5]
        df['b']=[2,3]
  
        with self.assertRaises(Exception) as cm:
            df.sort(42)

        self.assertEqual(str(cm.exception),
                         "'int' object is not iterable")
        
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_sort)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
