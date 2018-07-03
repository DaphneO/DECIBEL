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
from pyvttbl.tests.support import *

class Test_writeTable(unittest.TestCase):
    def setUp(self):
        self.df=DataFrame()
        self.df.read_tbl('data/suppression~subjectXgroupXageXcycleXphase.csv')

    def test0(self):
        d='data/suppression~subjectXgroupXageXcycleXphase.csv'
        r='subjectXsexXageXgroupXcycleXphaseXsuppressionXranddata.csv'
        self.df.write()
        self.assertTrue(fcmp(d,r))

        # clean up
        os.remove('./subjectXsexXageXgroupXcycleXphaseXsuppressionXranddata.csv')        

    def test1(self):
        # with exclusion
        d='data/suppression~subjectXgroupXageXcycleXphase.csv'
        r='subjectXsexXageXgroupXcycleXphaseXsuppressionXranddata.csv'
        self.df.write(where=[('AGE','not in',['young'])])
        self.assertTrue(fcmp(d,r))

        # clean up
        os.remove('./subjectXsexXageXgroupXcycleXphaseXsuppressionXranddata.csv') 
               
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_writeTable)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
