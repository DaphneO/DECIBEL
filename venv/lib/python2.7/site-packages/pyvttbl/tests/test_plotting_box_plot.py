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
from pyvttbl.plotting import box_plot
from pyvttbl.misc.support import *


class Test_box_plot(unittest.TestCase):
    def test0(self):
        R = {'d': [9.0, 8.0, 6.0, 8.0, 10.0, 4.0, 6.0, 5.0, 7.0, 7.0,
                   7.0, 9.0, 6.0, 6.0, 6.0, 11.0, 6.0, 3.0, 8.0, 7.0,
                   11.0, 13.0, 8.0, 6.0, 14.0, 11.0, 13.0, 13.0, 10.0,
                   11.0, 12.0, 11.0, 16.0, 11.0, 9.0, 23.0, 12.0, 10.0,
                   19.0, 11.0, 10.0, 19.0, 14.0, 5.0, 10.0, 11.0, 14.0,
                   15.0, 11.0, 11.0, 8.0, 6.0, 4.0, 6.0, 7.0, 6.0, 5.0,
                   7.0, 9.0, 7.0, 10.0, 7.0, 8.0, 10.0, 4.0, 7.0, 10.0,
                   6.0, 7.0, 7.0, 14.0, 11.0, 18.0, 14.0, 13.0, 22.0, 17.0,
                   16.0, 12.0, 11.0, 20.0, 16.0, 16.0, 15.0, 18.0, 16.0,
                   20.0, 22.0, 14.0, 19.0, 21.0, 19.0, 17.0, 15.0, 22.0,
                   16.0, 22.0, 22.0, 18.0, 21.0],
             'fname': 'output\\box(WORDS).png',
             'maintitle': 'WORDS',
             'val': 'WORDS'}
        
        df=DataFrame()
        df.TESTMODE=True
        df.read_tbl('data/words~ageXcondition.csv')
        D=df.box_plot('WORDS', output_dir='output')
        
        self.assertEqual(D['fname'],R['fname'])
        self.assertEqual(D['maintitle'],R['maintitle'])
        self.assertEqual(D['val'],R['val'])
        
        for d,r in zip(np.array(D['d']).flat,
                       np.array(R['d']).flat):
            self.assertAlmostEqual(d,r)        

    def test1(self):
        R = {'d': [np.array([ 9,  8,  6,  8, 10,  4,  6,  5,  7,  7,
                              7,  9,  6,  6,  6, 11,  6,  3,  8,  7,
                              11, 13,  8,  6, 14, 11, 13, 13, 10, 11,
                              12, 11, 16, 11,  9, 23, 12, 10, 19, 11,
                              10, 19, 14,  5, 10, 11, 14, 15, 11, 11]),
                   np.array([ 8,  6,  4,  6,  7,  6,  5,  7,  9,  7,
                              10,  7,  8, 10,  4,  7, 10, 6,  7,  7,
                              14, 11, 18, 14, 13, 22, 17, 16, 12, 11,
                              20, 16, 16, 15, 18, 16, 20, 22, 14, 19,
                              21, 19, 17, 15, 22, 16, 22, 22, 18, 21])],
             'fname': 'output\\box(WORDS~AGE).png',
             'maintitle': 'WORDS by AGE',
             'xlabels': [u'AGE = old', u'AGE = young']}
        
        df=DataFrame()
        df.TESTMODE=True
        df.read_tbl('data/words~ageXcondition.csv')
        D=df.box_plot('WORDS',['AGE'], output_dir='output')

        self.assertEqual(D['fname'],R['fname'])
        self.assertEqual(D['maintitle'],R['maintitle'])
        self.assertEqual(D['xlabels'],R['xlabels'])
        
        for d,r in zip(np.array(D['d']).flat,
                       np.array(R['d']).flat):
            self.assertAlmostEqual(d,r)

    def test2(self):
        R = {'d': [np.array([11, 13,  8,  6, 14, 11, 13, 13, 10, 11]),
                   np.array([ 9,  8,  6,  8, 10,  4,  6,  5,  7,  7]),
                   np.array([12, 11, 16, 11,  9, 23, 12, 10, 19, 11]),
                   np.array([10, 19, 14,  5, 10, 11, 14, 15, 11, 11]),
                   np.array([ 7,  9,  6,  6,  6, 11,  6,  3,  8,  7]),
                   np.array([14, 11, 18, 14, 13, 22, 17, 16, 12, 11]),
                   np.array([8, 6, 4, 6, 7, 6, 5, 7, 9, 7]),
                   np.array([20, 16, 16, 15, 18, 16, 20, 22, 14, 19]),
                   np.array([21, 19, 17, 15, 22, 16, 22, 22, 18, 21]),
                   np.array([10,  7,  8, 10,  4,  7, 10,  6,  7,  7])],
             'fname': 'output\\box(WORDS~AGE_X_CONDITION).png',
             'maintitle': 'WORDS by AGE * CONDITION',
             'xlabels': [u'AGE = old\nCONDITION = adjective',
                         u'AGE = old\nCONDITION = counting',
                         u'AGE = old\nCONDITION = imagery',
                         u'AGE = old\nCONDITION = intention',
                         u'AGE = old\nCONDITION = rhyming',
                         u'AGE = young\nCONDITION = adjective',
                         u'AGE = young\nCONDITION = counting',
                         u'AGE = young\nCONDITION = imagery',
                         u'AGE = young\nCONDITION = intention',
                         u'AGE = young\nCONDITION = rhyming']}
        
        df=DataFrame()
        df.TESTMODE=True
        df.read_tbl('data/words~ageXcondition.csv')
        D=df.box_plot('WORDS',['AGE','CONDITION'], output_dir='output')

        self.assertEqual(D['fname'],R['fname'])
        self.assertEqual(D['maintitle'],R['maintitle'])
        self.assertEqual(D['xlabels'],R['xlabels'])
        
        for d,r in zip(np.array(D['d']).flat,
                       np.array(R['d']).flat):
            self.assertAlmostEqual(d,r)

    def test3(self):
        df=DataFrame()
  
        with self.assertRaises(Exception) as cm:
            df.box_plot('a', output_dir='output')

        self.assertEqual(str(cm.exception),
                         'Table must have data to print data')

    def test4(self):
        df=DataFrame()
        df['a']=[2]
        df['b']=[2,3]
  
        with self.assertRaises(Exception) as cm:
            df.box_plot('a', output_dir='output')

        self.assertEqual(str(cm.exception),
                         'columns have unequal lengths')

    def test5(self):
        df=DataFrame()
        df['a']=[2,5]
        df['b']=[2,3]
  
        with self.assertRaises(Exception) as cm:
            df.box_plot('a',42, output_dir='output')

        self.assertEqual(str(cm.exception),
                         "'int' object is not iterable")
        
    def test6(self):
        df=DataFrame()
        df['a']=[2,5]
        df['b']=[2,3]
  
        with self.assertRaises(KeyError) as cm:
            df.box_plot('c', output_dir='output')

        self.assertEqual(str(cm.exception),"'c'")


def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_box_plot)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
