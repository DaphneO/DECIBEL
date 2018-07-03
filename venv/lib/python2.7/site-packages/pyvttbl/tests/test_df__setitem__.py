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

from collections import OrderedDict

import numpy as np

from pyvttbl import DataFrame
from pyvttbl.misc.support import *

class Test__setitem__(unittest.TestCase):
    def test1(self):
        R = {'DUM': 'integer',
          'COURSE': 'text',
           'ERROR': 'integer',
           'MODEL': 'text',
       'TIMEOFDAY': 'text',
         'SUBJECT': 'integer'}
        
        df=DataFrame()
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        df['DUM']=range(48) # Shouldn't complain

        self.assertEqual(df.keys(),
            ['SUBJECT', 'TIMEOFDAY', 'COURSE', 'MODEL', 'ERROR', 'DUM'])

        for k in R:
            self.assertEqual(df._sqltypesdict[k],R[k])

        
    def test11(self):
        df=DataFrame()
        df['DUM']=range(48) # Shouldn't complain
        self.assertEqual(df.keys(),['DUM'])

    def test12(self):
        df=DataFrame()
        df['DUM']=range(48) # Shouldn't complain
        self.assertEqual(df.keys(),['DUM'])
        
        df['DUM']=['A' for i in range(48)] # Shouldn't complain
        self.assertEqual(df.keys(),['DUM'])
        self.assertEqual(df._sqltypesdict['DUM'],'text')
        

    def test21(self):
        df=DataFrame()
        df[1]=range(48)
        df[2]=['A' for i in range(48)]
        self.assertEqual(df.keys(),[1,2])

    def test2(self):
        df=DataFrame()
        with self.assertRaises(TypeError) as cm:
            df['DUM']=42

        self.assertEqual(str(cm.exception),
                         "'int' object is not iterable")

## as of v 0.4.2.2 case variants are allowed
##    def test4(self):
##        df=DataFrame()
##        df['DUM']=[42]
##        with self.assertRaises(Exception) as cm:
##            df['dum']=[42]
##
##        self.assertEqual(str(cm.exception),
##                         "a case variant of 'dum' already exists")

    def test_kn(self):
        df = DataFrame()
        df.read_tbl('data/example.csv')
        y = [23]*len(df['X'])
        df['X'] = y
        
        self.assertEqual(df.keys(), ['CASE', 'TIME', 'CONDITION', 'X'])
        
    def test3(self):
        R = """c   b{L@^hsa aj}   a(1%32@) 
===========================
1   a                    34 
2   b                    34 
3   c                    42 
4   d                    34 
5   e                    45 
6   f                    34 """
        df=DataFrame()
        df.PRINTQUERIES = True
        df.insert({'a(1%32@)':34,'b{L@^hsa aj}':'a','c':1})
        df.insert({'a(1%32@)':34,'b{L@^hsa aj}':'b','c':2})
        df.insert({'a(1%32@)':42,'b{L@^hsa aj}':'c','c':3})
        df.insert({'a(1%32@)':34,'b{L@^hsa aj}':'d','c':4})
        df.insert({'a(1%32@)':45,'b{L@^hsa aj}':'e','c':5})
        df.insert({'a(1%32@)':34,'b{L@^hsa aj}':'f','c':6})

        self.assertEqual(R, str(df))

    def test3(self):

        tupa = ('a1','a2','a3')
        tupb = ('a1','b2','b3')
        
        df=DataFrame()
        df.insert([(('a1','a2','a3'),34), (('a1','b2','b3'),1)])
        df.insert([(('a1','a2','a3'),34), (('a1','b2','b3'),2)])
        df.insert([(('a1','a2','a3'),42), (('a1','b2','b3'),3)])

        namea,nameb = df.keys()
        
        self.assertEqual(namea, tupa)
        self.assertEqual(nameb, tupb)

def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test__setitem__)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
