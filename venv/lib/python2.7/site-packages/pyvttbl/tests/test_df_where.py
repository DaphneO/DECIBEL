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

class Test_where(unittest.TestCase):
    def test0(self):
        R = DataFrame([('SUBJECT', [1, 2]),
                        ('TIMEOFDAY', [u'T1', u'T1']),
                        ('COURSE', [u'C1', u'C2']),
                        ('MODEL', [u'M1', u'M1']),
                        ('ERROR', [10, 10])])
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        df2 = df.where('ERROR = 10')
        self.assertEqual(repr(df2), repr(R))

    def test1(self):
        R = DataFrame([('SUBJECT', [1, 2]),
                       ('TIMEOFDAY', [u'T1', u'T1']),
                       ('COURSE', [u'C1', u'C2']),
                       ('MODEL', [u'M1', u'M1']),
                       ('ERROR', [10, 10])])
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        df2 = df.where(['ERROR = 10'])
        self.assertEqual(repr(df2), repr(R))
    def test2(self):
        R = DataFrame([('SUBJECT', [1, 2]), ('TIMEOFDAY', [u'T1', u'T1']), ('COURSE', [u'C1', u'C2']), ('MODEL', [u'M1', u'M1']), ('ERROR', [10, 10])])
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        df2 = df.where([('ERROR', '=', 10)])
        self.assertEqual(repr(df2),repr(df2))
        
    def test3(self):
        R = DataFrame([('SUBJECT', [1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 3, 3, 3]), ('TIMEOFDAY', [u'T1', u'T1', u'T1', u'T2', u'T2', u'T2', u'T2', u'T2', u'T2', u'T1', u'T1', u'T1', u'T2', u'T2', u'T2']), ('COURSE', [u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1']), ('MODEL', [u'M1', u'M2', u'M3', u'M1', u'M2', u'M3', u'M1', u'M2', u'M3', u'M1', u'M2', u'M3', u'M1', u'M2', u'M3']), ('ERROR', [10, 8, 6, 5, 4, 3, 4, 3, 3, 8, 7, 4, 4, 1, 2])])
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        df2 = df.where('COURSE = "C1" and TIMEOFDAY in ("T1", "T2")')
        self.assertEqual(repr(df2),repr(df2))
        
    def test5(self):
        R = DataFrame([('SUBJECT', [1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 3, 3, 3]), ('TIMEOFDAY', [u'T1', u'T1', u'T1', u'T2', u'T2', u'T2', u'T2', u'T2', u'T2', u'T1', u'T1', u'T1', u'T2', u'T2', u'T2']), ('COURSE', [u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1']), ('MODEL', [u'M1', u'M2', u'M3', u'M1', u'M2', u'M3', u'M1', u'M2', u'M3', u'M1', u'M2', u'M3', u'M1', u'M2', u'M3']), ('ERROR', [10, 8, 6, 5, 4, 3, 4, 3, 3, 8, 7, 4, 4, 1, 2])])
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        df2 = df.where(['COURSE = "C1"','TIMEOFDAY in ("T1", "T2")'])
        self.assertEqual(repr(df2),repr(R))
        
    def test6(self):
        R = DataFrame([('SUBJECT', [1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 3, 3, 3]), ('TIMEOFDAY', [u'T1', u'T1', u'T1', u'T2', u'T2', u'T2', u'T2', u'T2', u'T2', u'T1', u'T1', u'T1', u'T2', u'T2', u'T2']), ('COURSE', [u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1', u'C1']), ('MODEL', [u'M1', u'M2', u'M3', u'M1', u'M2', u'M3', u'M1', u'M2', u'M3', u'M1', u'M2', u'M3', u'M1', u'M2', u'M3']), ('ERROR', [10, 8, 6, 5, 4, 3, 4, 3, 3, 8, 7, 4, 4, 1, 2])])
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        df2 = df.where([('COURSE','=',['C1']),('TIMEOFDAY','in',["T1", "T2"])])
        self.assertEqual(repr(df2),repr(R))
        
        
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_where)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
