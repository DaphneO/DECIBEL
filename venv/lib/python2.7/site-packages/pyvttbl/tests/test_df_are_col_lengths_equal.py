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

class Test__are_col_lengths_equal(unittest.TestCase):
    def test0(self):
        """emtpy table"""
        df=DataFrame()
        self.assertTrue(df._are_col_lengths_equal())

    def test1(self):
        """emtpy lists in table"""
        df=DataFrame()
        df[1]=[]
        df[2]=[]
        self.assertTrue(df._are_col_lengths_equal())

    def test2(self):
        """equal non-zero"""
        df=DataFrame()
        df[1]=range(10)
        df[2]=range(10)
        df[3]=range(10)
        df[4]=range(10)
        self.assertTrue(df._are_col_lengths_equal())

    def test3(self):
        """unequal"""
        df=DataFrame()
        df[1]=range(10)
        df[2]=range(10)
        df[3]=range(10)
        df[4]=range(9)
        self.assertFalse(df._are_col_lengths_equal())
        
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test__are_col_lengths_equal)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
