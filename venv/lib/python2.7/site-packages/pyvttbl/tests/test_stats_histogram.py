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
##from pyvttbl.plotting import box_plot
from pyvttbl.misc.support import *
        
class Test_histogram(unittest.TestCase):
    def test0(self):
        R=[[4.0, 14.0, 17.0, 12.0, 15.0, 10.0, 9.0, 5.0, 6.0, 8.0],
           [3.0, 5.0, 7.0, 9.0, 11.0, 13.0, 15.0, 17.0, 19.0, 21.0, 23.0]]
        
        df=DataFrame()
        df.read_tbl('data/words~ageXcondition.csv')
        D=df.histogram('WORDS')
        D=[D['values'],D['bin_edges']]

        for (d,r) in zip(_flatten(D),_flatten(R)):
            self.assertAlmostEqual(d,r)

    def test01(self):
        df=DataFrame()
        df.read_tbl('data/words~ageXcondition.csv')
        D=str(df.histogram('WORDS',cumulative=True))
        R = """\
Cumulative Histogram for WORDS
 Bins    Values  
================
 3.000     4.000 
 5.000    18.000 
 7.000    35.000 
 9.000    47.000 
11.000    62.000 
13.000    72.000 
15.000    81.000 
17.000    86.000 
19.000    92.000 
21.000   100.000 
23.000           """
        self.assertEqual(D, R)
        
    def test02(self):
        df=DataFrame()
        df.read_tbl('data/words~ageXcondition.csv')
        D = repr(df.histogram('WORDS'))
        R = "Histogram([('values', [4.0, 14.0, 17.0, 12.0, 15.0, 10.0, 9.0, 5.0, 6.0, 8.0]), \
('bin_edges', [3, 5.0, 7.0, 9.0, 11.0, 13.0, 15.0, 17.0, 19.0, 21.0, 23])], cname='WORDS')"
        self.assertEqual(D, R)
        
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_histogram)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
