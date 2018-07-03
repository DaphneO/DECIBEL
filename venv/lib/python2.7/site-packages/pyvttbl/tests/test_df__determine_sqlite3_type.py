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

class Test__checktype(unittest.TestCase):
    def test0(self):
        df=DataFrame()
        df[1]=[]
        self.assertEqual(df._determine_sqlite3_type(df[1]),'null')

    def test1(self):
        df=DataFrame()
        df[1]=[1,2,3.,5.,8.]
        self.assertEqual(df._determine_sqlite3_type(df[1]),'integer')

    def test2(self):
        df=DataFrame()
        df[1]=[1,2,3.,5.,8.]
        self.assertEqual(df._determine_sqlite3_type(df[1]),'integer')

    def test3(self):
        df=DataFrame()
        df[1]=[1,2,3.,5.,8.0001]
        self.assertEqual(df._determine_sqlite3_type(df[1]),'real')

    def test4(self):
        df=DataFrame()
        df[1]=[1e4,3e3,5e1,6e0]
        self.assertEqual(df._determine_sqlite3_type(df[1]),'integer')

    def test5(self):
        df=DataFrame()
        df[1]=[1e4,3e3,5e1,6.001e0]
        self.assertEqual(df._determine_sqlite3_type(df[1]),'real')
        
    def test6(self):
        df=DataFrame()
        df[1]=[1,2,3.,5.,8.0001,'a']
        self.assertEqual(df._determine_sqlite3_type(df[1]),'text')
        
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test__checktype)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
