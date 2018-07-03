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

from pyvttbl import DataFrame, PyvtTbl
from pyvttbl.misc.support import *

class Test_pivot_0(unittest.TestCase):
                    
    def test1(self):
        """method='valid', aggregate=count, invalid row"""
        
        R = """\
count(id)
Name    Year   member=N   member=Y   Total 
==========================================
name1   2010          0          1       1 
name1   2011          1          0       1 
name2   2011          0          1       1 
==========================================
Total                 1          2       3 """
        
        df = DataFrame()
        df.insert({'id':0,'Name':'name1','Year':2010,'member':'Y'})
        df.insert({'id':1,'Name':'name1','Year':2011,'member':'N'})
        df.insert({'id':2,'Name':'name2','Year':2011,'member':'Y'})
        
        my_pivot = df.pivot('id',rows = ['Name','Year'], cols = ['member'], aggregate='count')

        self.assertEqual(R,str(my_pivot))
        
    def test2(self):
        """method='valid', aggregate=count, invalid col"""
        
        R = """\
count(id)
member   Name=name1,   Name=name1,   Name=name2,   Total 
          Year=2010     Year=2011     Year=2011          
========================================================
N                  0             1             0       1 
Y                  1             0             1       2 
========================================================
Total              1             1             1       3 """
        
        df = DataFrame()
        df.insert({'id':0,'Name':'name1','Year':2010,'member':'Y'})
        df.insert({'id':1,'Name':'name1','Year':2011,'member':'N'})
        df.insert({'id':2,'Name':'name2','Year':2011,'member':'Y'})
        
        my_pivot = df.pivot('id',rows = ['member'], cols = ['Name','Year'], aggregate='count')
        
        self.assertEqual(R,str(my_pivot))

    def test3(self):
        """method='full', aggregate=count, invalid row"""
        
        R = """\
count(id)
Name    Year   member=N   member=Y   Total 
==========================================
name1   2010          0          1       1 
name1   2011          1          0       1 
name2   2010         --         --      -- 
name2   2011          0          1       1 
==========================================
Total                 1          2       3 """
        
        df = DataFrame()
        df.insert({'id':0,'Name':'name1','Year':2010,'member':'Y'})
        df.insert({'id':1,'Name':'name1','Year':2011,'member':'N'})
        df.insert({'id':2,'Name':'name2','Year':2011,'member':'Y'})
        
        my_pivot = df.pivot('id',rows = ['Name','Year'], cols = ['member'],
                            aggregate='count', method='full')
        
        self.assertEqual(R,str(my_pivot))
        
    def test4(self):
        """method='full', aggregate=count, invalid row"""

        R = """\
count(id)
member   Name=name1,   Name=name1,   Name=name2,   Name=name2,   Total 
          Year=2010     Year=2011     Year=2010     Year=2011          
======================================================================
N                  0             1            --             0       1 
Y                  1             0            --             1       2 
======================================================================
Total              1             1            --             1       3 """
        
        df = DataFrame()
        df.insert({'id':0,'Name':'name1','Year':2010,'member':'Y'})
        df.insert({'id':1,'Name':'name1','Year':2011,'member':'N'})
        df.insert({'id':2,'Name':'name2','Year':2011,'member':'Y'})
        
        my_pivot = df.pivot('id',rows = ['member'], cols = ['Name','Year'],
                            aggregate='count', method='full')

        self.assertEqual(R,str(my_pivot))

class Test_pivot_1(unittest.TestCase):
    def test1(self):        
        """method='valid', aggregate=tolist, invalid row"""
        R = """\
tolist(id)
Name    Year     member=N       member=Y   
==========================================
name1   2010   [None, None]     [0.0, 0.0] 
name1   2011     [1.0, 1.0]   [None, None] 
name2   2011   [None, None]     [2.0, 2.0] """
        
        df = DataFrame()
        df.insert({'id':0,'Name':'name1','Year':2010,'member':'Y','rep':1})
        df.insert({'id':1,'Name':'name1','Year':2011,'member':'N','rep':1})
        df.insert({'id':2,'Name':'name2','Year':2011,'member':'Y','rep':1})
        df.insert({'id':0,'Name':'name1','Year':2010,'member':'Y','rep':2})
        df.insert({'id':1,'Name':'name1','Year':2011,'member':'N','rep':2})
        df.insert({'id':2,'Name':'name2','Year':2011,'member':'Y','rep':2})
        
        my_pivot = df.pivot('id',rows = ['Name','Year'], cols = ['member'],
                            aggregate='tolist')

##        print(my_pivot)
        
        self.assertEqual(R,str(my_pivot))
        
    def test2(self):
        """method='valid', aggregate=tolist, invalid col"""
    
        R = """\
tolist(id)
member   Name=name1,    Name=name1,    Name=name2,  
          Year=2010      Year=2011      Year=2011   
===================================================
N        [None, None]     [1.0, 1.0]   [None, None] 
Y          [0.0, 0.0]   [None, None]     [2.0, 2.0] """
        
        df = DataFrame()
        df.insert({'id':0,'Name':'name1','Year':2010,'member':'Y','rep':1})
        df.insert({'id':1,'Name':'name1','Year':2011,'member':'N','rep':1})
        df.insert({'id':2,'Name':'name2','Year':2011,'member':'Y','rep':1})
        df.insert({'id':0,'Name':'name1','Year':2010,'member':'Y','rep':2})
        df.insert({'id':1,'Name':'name1','Year':2011,'member':'N','rep':2})
        df.insert({'id':2,'Name':'name2','Year':2011,'member':'Y','rep':2})
        
        my_pivot = df.pivot('id',rows = ['member'], cols = ['Name','Year'],
                            aggregate='tolist')
        
##        print(my_pivot)
        
        self.assertEqual(R,str(my_pivot))

    def test3(self):
        """method='full', aggregate=tolist, invalid row"""
        
        R = """\
tolist(id)
Name    Year     member=N       member=Y   
==========================================
name1   2010   [None, None]     [0.0, 0.0] 
name1   2011     [1.0, 1.0]   [None, None] 
name2   2010   [None, None]   [None, None] 
name2   2011   [None, None]     [2.0, 2.0] """
        
        df = DataFrame()
        df.insert({'id':0,'Name':'name1','Year':2010,'member':'Y','rep':1})
        df.insert({'id':1,'Name':'name1','Year':2011,'member':'N','rep':1})
        df.insert({'id':2,'Name':'name2','Year':2011,'member':'Y','rep':1})
        df.insert({'id':0,'Name':'name1','Year':2010,'member':'Y','rep':2})
        df.insert({'id':1,'Name':'name1','Year':2011,'member':'N','rep':2})
        df.insert({'id':2,'Name':'name2','Year':2011,'member':'Y','rep':2})
        
        my_pivot = df.pivot('id',rows = ['Name','Year'], cols = ['member'],
                            aggregate='tolist', method='full')
        

##        print(my_pivot)

        self.assertEqual(R,str(my_pivot))
        
    def test4(self):
        """method='full', aggregate=tolist, invalid col"""
        
        R = """\
tolist(id)
member   Name=name1,    Name=name1,    Name=name2,    Name=name2,  
          Year=2010      Year=2011      Year=2010      Year=2011   
==================================================================
N        [None, None]     [1.0, 1.0]   [None, None]   [None, None] 
Y          [0.0, 0.0]   [None, None]   [None, None]     [2.0, 2.0] """
        
        df = DataFrame()
        df.insert({'id':0,'Name':'name1','Year':2010,'member':'Y','rep':1})
        df.insert({'id':1,'Name':'name1','Year':2011,'member':'N','rep':1})
        df.insert({'id':2,'Name':'name2','Year':2011,'member':'Y','rep':1})
        df.insert({'id':0,'Name':'name1','Year':2010,'member':'Y','rep':2})
        df.insert({'id':1,'Name':'name1','Year':2011,'member':'N','rep':2})
        df.insert({'id':2,'Name':'name2','Year':2011,'member':'Y','rep':2})
        
        my_pivot = df.pivot('id',rows = ['member'], cols = ['Name','Year'],
                            aggregate='tolist', method='full')

##        print(my_pivot)

        self.assertEqual(R,str(my_pivot))
    
class Test_pivot_2(unittest.TestCase):
    def setUp(self):
        D={
            'SUBJECT':[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100],
            'AGE':'old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,old,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young,young'.split(','),
            'CONDITION':'counting,counting,counting,counting,counting,counting,counting,counting,counting,counting,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,intention,intention,intention,intention,intention,intention,intention,intention,intention,intention,counting,counting,counting,counting,counting,counting,counting,counting,counting,counting,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,rhyming,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,adjective,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,imagery,intention,intention,intention,intention,intention,intention,intention,intention,intention,intention'.split(','),
            'WORDS':[9,8,6,8,10,4,6,5,7,7,7,9,6,6,6,11,6,3,8,7,11,13,8,6,14,11,13,13,10,11,12,11,16,11,9,23,12,10,19,11,10,19,14,5,10,11,14,15,11,11,8,6,4,6,7,6,5,7,9,7,10,7,8,10,4,7,10,6,7,7,14,11,18,14,13,22,17,16,12,11,20,16,16,15,18,16,20,22,14,19,21,19,17,15,22,16,22,22,18,21],
           }
        
        self.df=DataFrame()
        self.df.read_tbl('data/words~ageXcondition.csv')
        
    def test001(self):
        with self.assertRaises(KeyError) as cm:
            self.df.pivot('NOTAKEY',rows=['AGE'])

        self.assertEqual(str(cm.exception),"'NOTAKEY'")
        
    def test002(self):
        with self.assertRaises(KeyError) as cm:
            self.df.pivot('CONDITION',cols=['NOTAKEY'])

        self.assertEqual(str(cm.exception),"'NOTAKEY'")

    def test003(self):
        with self.assertRaises(KeyError) as cm:
            self.df.pivot('SUBJECT',rows=['NOTAKEY','AGE'])

        self.assertEqual(str(cm.exception),"'NOTAKEY'")

    def test004(self):
        with self.assertRaises(KeyError) as cm:
            self.df.pivot('CONDITION',cols=['NOTAKEY'])

        self.assertEqual(str(cm.exception),"'NOTAKEY'")

##    def test005(self):
##        with self.assertRaises(TypeError) as cm:
##            self.df.pivot('SUBJECT',rows='AGE')
##
##        self.assertEqual(str(cm.exception),
##                         "'str' object is not iterable")

    def test0051(self):
        with self.assertRaises(TypeError) as cm:
            self.df.pivot('SUBJECT',rows=42)

        self.assertEqual(str(cm.exception),
                         "'list' object is not iterable")
        
    def test006(self):
        with self.assertRaises(TypeError) as cm:
            self.df.pivot('SUBJECT',cols='AGE')

        self.assertEqual(str(cm.exception),
                         "'str' object is not iterable")
        
##    def test004(self):
##        # test the exclude parameter checking
##
##        with warnings.catch_warnings(record=True) as w:
##            # Cause all warnings to always be triggered.
##            warnings.simplefilter("always")
##            
##            # Trigger a warning.    
##            self.df.pivot('SUBJECT',
##                          where=[('AGE','not in',['medium',])])
##        
##            assert issubclass(w[-1].category, RuntimeWarning)
    
    def test005(self):
        # test the exclude parameter
        R=np.array([[14.8], [6.5], [17.6], [19.3], [7.6]])
        
        # this one shouldn't raise an Exception
        D = self.df.pivot('WORDS',rows=['CONDITION'],
                      where=[('AGE','not in',['old',])])
        

        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)
        
    def test011(self):
        R=np.array([[25.5], [75.5]])
        
        # aggregate is case-insensitive
        D=self.df.pivot('SUBJECT',rows=['AGE'],aggregate='AVG')
        
        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)
        
    def test0(self):
        R=np.array([[ 11. ,   7. ,  13.4,  12. ,   6.9],
                 [ 14.8,   6.5,  17.6,  19.3,   7.6]])
        
        D = self.df.pivot('WORDS',rows=['AGE'],cols=['CONDITION'])
        
        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)

    def test1(self):
        R=np.array([[ 110.,  148.],
                    [  70.,   65.],
                    [ 134.,  176.],
                    [ 120.,  193.],
                    [  69.,   76.]])
        
        myPyvtTbl = self.df.pivot('WORDS',rows=['CONDITION'],cols=['AGE'],aggregate='sum')
        D=np.array(myPyvtTbl)
        
        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)

    def test3(self):
        R=np.array([[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                  11.0, 13.0, 8.0,  6.0,  14.0, 11.0, 13.0, 13.0, 10.0, 11.0, None, None, None, None, None, None, None, None, None, None,
                  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                  None, None, None, None, None, None, None, None, None, None, 14.0, 11.0, 18.0, 14.0, 13.0, 22.0, 17.0, 16.0, 12.0, 11.0,
                  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                 [9.0,  8.0,  6.0,  8.0,  10.0, 4.0,  6.0,  5.0,  7.0,  7.0,  None, None, None, None, None, None, None, None, None, None,
                  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                  None, None, None, None, None, None, None, None, None, None, 8.0,  6.0,  4.0,  6.0,  7.0,  6.0,  5.0,  7.0,  9.0,  7.0,
                  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                 [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                  None, None, None, None, None, None, None, None, None, None, 12.0, 11.0, 16.0, 11.0, 9.0, 23.0, 12.0, 10.0, 19.0, 11.0,
                  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                  20.0, 16.0, 16.0, 15.0, 18.0, 16.0, 20.0, 22.0, 14.0, 19.0, None, None, None, None, None, None, None, None, None, None],
                 [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                  10.0, 19.0, 14.0, 5.0,  10.0, 11.0, 14.0, 15.0, 11.0, 11.0, None, None, None, None, None, None, None, None, None, None,
                  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                  None, None, None, None, None, None, None, None, None, None, 21.0, 19.0, 17.0, 15.0, 22.0, 16.0, 22.0, 22.0, 18.0, 21.0],
                 [None, None, None, None, None, None, None, None, None, None, 7.0,  9.0,  6.0,  6.0,  6.0,  11.0, 6.0,  3.0,  8.0,  7.0,
                  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                  10.0, 7.0,  8.0,  10.0, 4.0,  7.0,  10.0, 6.0,  7.0,  7.0,  None, None, None, None, None, None, None, None, None, None,
                  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]], dtype=object)

        # One row and one col factor                     
        D=self.df.pivot('WORDS',rows=['CONDITION'],cols=['SUBJECT'],aggregate='sum')
        
        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)

    def test4(self):
        R=np.array([[5.191085988]])

        # No rows or cols        
        D = self.df.pivot('WORDS',aggregate='stdev')
        
        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)

    def test5(self):
        # when the tolist aggregate the pivot operation
        # uses eval to unpack the lists
        R=np.array([[[11.0, 13.0, 8.0, 6.0, 14.0, 11.0, 13.0, 13.0, 10.0, 11.0],
                  [9.0, 8.0, 6.0, 8.0, 10.0, 4.0, 6.0, 5.0, 7.0, 7.0],
                  [12.0, 11.0, 16.0, 11.0, 9.0, 23.0, 12.0, 10.0, 19.0, 11.0],
                  [10.0, 19.0, 14.0, 5.0, 10.0, 11.0, 14.0, 15.0, 11.0, 11.0],
                  [7.0, 9.0, 6.0, 6.0, 6.0, 11.0, 6.0, 3.0, 8.0, 7.0]],
                 [[14.0, 11.0, 18.0, 14.0, 13.0, 22.0, 17.0, 16.0, 12.0, 11.0],
                  [8.0, 6.0, 4.0, 6.0, 7.0, 6.0, 5.0, 7.0, 9.0, 7.0],
                  [20.0, 16.0, 16.0, 15.0, 18.0, 16.0, 20.0, 22.0, 14.0, 19.0],
                  [21.0, 19.0, 17.0, 15.0, 22.0, 16.0, 22.0, 22.0, 18.0, 21.0],
                  [10.0, 7.0, 8.0, 10.0, 4.0, 7.0, 10.0, 6.0, 7.0, 7.0]]])

        D = self.df.pivot('WORDS',
                      rows=['AGE'], cols=['CONDITION'],
                      aggregate='tolist')

##        print(D)

        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)

    def test6(self):
        # tolist handles text data differently then integer
        # or float data. We need to test this case as well
        R=np.array([[['L', 'N', 'I', 'G', 'O', 'L', 'N', 'N', 'K', 'L'],
                  ['J', 'I', 'G', 'I', 'K', 'E', 'G', 'F', 'H', 'H'],
                  ['M', 'L', 'Q', 'L', 'J', 'X', 'M', 'K', 'T', 'L'],
                  ['K', 'T', 'O', 'F', 'K', 'L', 'O', 'P', 'L', 'L'],
                  ['H', 'J', 'G', 'G', 'G', 'L', 'G', 'D', 'I', 'H']],
                 [['O', 'L', 'S', 'O', 'N', 'W', 'R', 'Q', 'M', 'L'],
                  ['I', 'G', 'E', 'G', 'H', 'G', 'F', 'H', 'J', 'H'],
                  ['U', 'Q', 'Q', 'P', 'S', 'Q', 'U', 'W', 'O', 'T'],
                  ['V', 'T', 'R', 'P', 'W', 'Q', 'W', 'W', 'S', 'V'],
                  ['K', 'H', 'I', 'K', 'E', 'H', 'K', 'G', 'H', 'H']]])

        # caesar cipher
        num2abc=dict(zip(list(range(26)),'ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
        self.df['ABC']=[num2abc[v%26] for v in self.df['WORDS']]

        D = self.df.pivot('ABC',
                      rows=['AGE'], cols=['CONDITION'],
                      aggregate='tolist')
    
        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)

    def test7(self):
        # test group_concat
        R=np.array( [[u'11,13,8,6,14,11,13,13,10,11',
                      u'9,8,6,8,10,4,6,5,7,7',
                      u'12,11,16,11,9,23,12,10,19,11',
                      u'10,19,14,5,10,11,14,15,11,11',
                      u'7,9,6,6,6,11,6,3,8,7'],
                     [u'14,11,18,14,13,22,17,16,12,11',
                      u'8,6,4,6,7,6,5,7,9,7',
                      u'20,16,16,15,18,16,20,22,14,19',
                      u'21,19,17,15,22,16,22,22,18,21',
                      u'10,7,8,10,4,7,10,6,7,7']])

        D=self.df.pivot('WORDS',
                      rows=['AGE'], cols=['CONDITION'],
                      aggregate='group_concat')

        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessEqual(d,r)
            
class Test_pivot_3(unittest.TestCase):
    def setUp(self):
        self.df=DataFrame()
        self.df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        
    def test0(self):
              # M 1  2  3
        R=np.array([[2, 2, 2],  # T1 C1
                 [3, 1, 2],  # T1 C2
                 [3, 3, 3],  # T1 C3
                 [3, 3, 3],  # T2 C1
                 [3, 3, 3],  # T2 C2
                 [3, 3, 3]]) # T2 C3

        myPyvtTbl = self.df.pivot('ERROR',rows=['TIMEOFDAY','COURSE'],
                      cols=['MODEL'],aggregate='count')

        D=np.array(myPyvtTbl)

        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)

    def test1(self):
        # check to make sure missing cells are correct
        R=np.array([[1, 1, 1, 1, 1, 1],
                 [1, 1, 0, 1, 0, 1],
                 [1, 1, 1, 1, 1, 1],
                 [0, 1, 0, 1, 0, 1],
                 [1, 1, 1, 1, 1, 1],
                 [1, 1, 1, 1, 1, 1],
                 [1, 1, 1, 1, 1, 1],
                 [1, 1, 0, 1, 1, 1],
                 [1, 1, 1, 1, 1, 1]])
        
        # multiple rows and cols
        myPyvtTbl = self.df.pivot('ERROR',rows=['SUBJECT','COURSE'],
                      cols=['MODEL','TIMEOFDAY'],aggregate='count')

        D=np.array(myPyvtTbl)

        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)

    def test2(self):          
        R=np.array([[ 0.26882528, -0.06797845]])

        # No row
        myPyvtTbl = self.df.pivot('ERROR',cols=['TIMEOFDAY'],aggregate='skew')
        D=np.array(myPyvtTbl)

        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)

    def test3(self):              
        R=np.array([[ 0.26882528],
                 [-0.06797845]])

        # No col
        myPyvtTbl = self.df.pivot('ERROR',rows=['TIMEOFDAY'],aggregate='skew')
        D=np.array(myPyvtTbl)
        
        # verify the table is the correct shape
        self.assertEqual(R.shape,D.shape)

        # verify the values in the table
        for d,r in zip(D.flat,R.flat):
            self.failUnlessAlmostEqual(d,r)

        
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_pivot_0),
            unittest.makeSuite(Test_pivot_1),
            unittest.makeSuite(Test_pivot_2),
            unittest.makeSuite(Test_pivot_3)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
