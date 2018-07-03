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

class Test_del_item(unittest.TestCase):
    def setUp(self):
        self.df=DataFrame()
        self.df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
    
        del self.df['COURSE']

    def test0(self):
        self.assertEqual(self.df.keys(),
                         ['SUBJECT', 'TIMEOFDAY', 'MODEL', 'ERROR'])

    def test1(self):
        self.assertEqual(list(self.df.types()),
                         ['integer', 'text', 'text', 'integer'])

    def test3(self):
        self.assertEqual(len(self.df), 4)
        
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_del_item)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
