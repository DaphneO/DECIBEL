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

class Test_read_tbl(unittest.TestCase):
    def test00(self):

        # skip 4 lines
        # DON'T MESS WITH THE SPACING
        with open('test.csv','wb') as f:
            f.write("""



x,y,z
1,5,9
2,6,10
3,7,11
4,8,12""")
            
        self.df=DataFrame()
        self.df.read_tbl('data/skiptest.csv',skip=4)
        D = list(self.df['x']) + \
            list(self.df['y']) + \
            list(self.df['z'])
        
        R=range(1,13)
        
        for (d,r) in zip(D,R):
            self.assertAlmostEqual(d,r)

    def test01(self):

        # no labels
        with open('test.csv','wb') as f:
            f.write("""
1,5,9
2,6,10
3,7,11
4,8,12""")
            
        self.df=DataFrame()
        self.df.read_tbl('test.csv',skip=1,labels=False)
        D = list(self.df['COL_1']) + \
            list(self.df['COL_2']) + \
            list(self.df['COL_3'])
        
        R=range(1,13)
        
        for (d,r) in zip(D,R):
            self.assertAlmostEqual(d,r)

    def test03(self):

        # duplicate labels
        with open('test.csv','wb') as f:
            f.write("""
x,x,x
1,5,9
2,6,10
3,7,11
4,8,12""")
            
        self.df=DataFrame()
        
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            
            # Trigger a warning.    
            self.df.read_tbl('test.csv',skip=1,labels=True)
        
            assert issubclass(w[-1].category, RuntimeWarning)
            
        D = list(self.df['x']) + \
            list(self.df['x_2'])+ \
            list(self.df['x_3'])
        R=range(1,13)
        
        for (d,r) in zip(D,R):
            self.assertAlmostEqual(d,r)

    def test04(self):

        # line missing data, no comma after 6
        with open('test.csv','wb') as f:
            f.write("""
x,y,z
1,5,9
2,6
3,7,11
4,8,12""")
            
        self.df=DataFrame()
        
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            
            # Trigger a warning.    
            self.df.read_tbl('test.csv',skip=1,labels=True)
        
            assert issubclass(w[-1].category, RuntimeWarning)
            
        D = list(self.df['x']) + \
            list(self.df['y']) + \
            list(self.df['z'])
        
        R=[1,3,4,5,7,8,9,11,12]
        
        for (d,r) in zip(D,R):
            self.assertAlmostEqual(d,r)

    def test05(self):
        R = """\
x   y   z  
==========
1   5    9 
2   6   -- 
3   7   11 
4   8   12 """

        # cell has empty string, comma after 6
        with open('test.csv','wb') as f:
            f.write("""
x,y,z
1,5,9
2,6,
3,7,11
4,8,12""")
            
        self.df=DataFrame()
        self.df.read_tbl('test.csv',skip=1,labels=True)

        self.assertAlmostEqual(str(self.df),R)

    def test06(self):
        R = """\
y 1   y 2   y 3 
===============
  1     5     9 
  2     6    -- 
  3     7    11 
  4     8    12 """

        # labels have spaces
        with open('test.csv','wb') as f:
            f.write("""
y 1,y 2,y 3
1,5,9
2,6,
3,7,11
4,8,12""")
            
        self.df=DataFrame()
        self.df.read_tbl('test.csv',skip=1,labels=True)
        
        self.assertAlmostEqual(str(self.df),R)
        
    def test07(self):

        # labels have spaces
        with open('test.csv','wb') as f:
            f.write("""
y 1,   y 2   ,   y 3
1,5,9
2,6,
3,7,11
4,8,12""")
            
        self.df=DataFrame()
        self.df.read_tbl('test.csv',skip=1,labels=True)

        print(self.df)

        for z in self.df['y 3']:
            print(type(z))
        
        D = list(self.df['y 1']) + \
            list(self.df['y 2']) + \
            list(self.df['y 3'])
               
        R=[1,2,3,4,5,6,7,8,9,np.ma.core.MaskedConstant(),11,12]
        
        for (d,r) in zip(D,R):
            self.assertEqual(str(d),str(r))
            
    def tearDown(self):
        os.remove('./test.csv')        

def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_read_tbl)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
