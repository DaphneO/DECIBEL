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

class Test_attach(unittest.TestCase):
    def test0(self):
        self.df1=DataFrame()
        self.df1.read_tbl('data/words~ageXcondition.csv')

        with self.assertRaises(Exception) as cm:
            self.df1.attach('s')

        self.assertEqual(str(cm.exception),
                         'second argument must be a DataFrame')
        
    def test1(self):
        self.df1=DataFrame()
        self.df2=DataFrame()
        self.df1.read_tbl('data/words~ageXcondition.csv')
        self.df2.read_tbl('data/words~ageXcondition.csv')

        # add an extra key to df1
        self.df1['EXTRA'] = [5 for a in self.df1['AGE']]

        with self.assertRaises(Exception) as cm:
            self.df1.attach(self.df2)

        self.assertEqual(str(cm.exception),
                         'self and other must have the same columns')

    def test2(self):
        df1=DataFrame()
        df2=DataFrame()
        df1.read_tbl('data/words~ageXcondition.csv')
        df2.read_tbl('data/words~ageXcondition.csv')

        M=df1.shape()[1]

        # this should work
        df1.attach(df2)

        # df1 should have twice as many rows now
        self.assertEqual(df1.shape()[1]/2,df2.shape()[1])

        # go through and check data
        for i in range(M):
            for n in df1.keys():
                if _isfloat(df1[n][i]):
                    self.assertAlmostEqual(df1[n][i],df1[n][M+i])
                else:
                    self.assertEqual(df1[n][i],df1[n][M+i])
                    
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_attach)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
