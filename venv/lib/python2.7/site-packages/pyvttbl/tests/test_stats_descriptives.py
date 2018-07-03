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

from pyvttbl import DataFrame
from pyvttbl.stats import Descriptives
from pyvttbl.misc.support import *

class Test_descriptives(unittest.TestCase):
    def test0(self):
        R = Descriptives([('count', 100.0),
                          ('mean', 11.61),
                          ('mode', 11.0),
                          ('var', 26.947373737373752),
                          ('stdev', 5.191085988246944),
                          ('sem', 0.5191085988246944),
                          ('rms', 12.707084638106414),
                          ('min', 3.0),
                          ('Q1', 7.0),
                          ('median', 11.0),
                          ('Q3', 15.5),
                          ('max', 23.0),
                          ('range', 20.0),
                          ('95ci_lower', 10.592547146303598),
                          ('95ci_upper', 12.6274528536964)],
                         cname='WORDS')

        df=DataFrame()
        df.read_tbl('data/words~ageXcondition.csv')

        D=df.descriptives('WORDS')
        
        for k in D.keys():
            self.failUnlessAlmostEqual(D[k],R[k])

    def test01(self):
        """repr test"""
        R = Descriptives([('count', 100.0),
                          ('mean', 11.61),
                          ('mode', 11.0),
                          ('var', 26.947373737373752),
                          ('stdev', 5.191085988246944),
                          ('sem', 0.5191085988246944),
                          ('rms', 12.707084638106414),
                          ('min', 3.0),
                          ('Q1', 7.0),
                          ('median', 11.0),
                          ('Q3', 15.5),
                          ('max', 23.0),
                          ('range', 20.0),
                          ('95ci_lower', 10.592547146303598),
                          ('95ci_upper', 12.6274528536964)],
                         cname='WORDS')
        
        df = DataFrame()
        df.read_tbl('data/words~ageXcondition.csv')
        D = eval(repr(df.descriptives('WORDS')))
        
        for k in D.keys():
            self.failUnlessAlmostEqual(D[k],R[k])

    def test02(self):
        df = DataFrame()
        df.read_tbl('data/words~ageXcondition.csv')
        D = str(df.descriptives('WORDS'))
        R = """\
Descriptive Statistics
  WORDS
==========================
 count        100.000 
 mean          11.610 
 mode          11.000 
 var           26.947 
 stdev          5.191 
 sem            0.519 
 rms           12.707 
 min            3.000 
 Q1             7.000 
 median        11.000 
 Q3            15.500 
 max           23.000 
 range         20.000 
 95ci_lower    10.593 
 95ci_upper    12.627 """
        self.assertEqual(D, R)
        
    def test1(self):
        R = Descriptives([('count', 48.0),
                          ('mean', 3.8958333333333335),
                          ('mode', 3.0),
                          ('var', 5.797429078014184),
                          ('stdev', 2.4077850979716158),
                          ('sem', 0.34753384361617046),
                          ('rms', 4.566636252940086),
                          ('min', 0.0),
                          ('Q1', 2.0),
                          ('median', 3.0),
                          ('Q3', 5.0),
                          ('max', 10.0),
                          ('range', 10.0),
                          ('95ci_lower', 3.2146669998456394),
                          ('95ci_upper', 4.5769996668210275)],
                         cname='ERROR')
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')

        D=df.descriptives('ERROR')
        
        for k in D.keys():
            self.failUnlessAlmostEqual(D[k],R[k])

    def test11(self):
        df = DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')

        D = str(df.descriptives('ERROR'))
        R = """\
Descriptive Statistics
  ERROR
==========================
 count        48.000 
 mean          3.896 
 mode          3.000 
 var           5.797 
 stdev         2.408 
 sem           0.348 
 rms           4.567 
 min           0.000 
 Q1            2.000 
 median        3.000 
 Q3            5.000 
 max          10.000 
 range        10.000 
 95ci_lower    3.215 
 95ci_upper    4.577 """
        self.assertEqual(D, R)

def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_descriptives),
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
