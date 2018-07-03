from __future__ import print_function

# Copyright (c) 2011, Roger Lew [see LICENSE.txt]
# This software is funded in part by NIH Grant P20 RR016454.

import unittest
import warnings
import os
import math
from random import shuffle, random
from collections import Counter,OrderedDict
from dictset import DictSet,_rep_generator
from math import isnan, isinf, floor
import numpy as np
from pprint import pprint as pp

from pyvttbl import PyvtTbl
from pyvttbl import DataFrame
from pyvttbl.plotting import *
from pyvttbl.stats import *
from pyvttbl.misc.support import *

class Test_chisquare1way(unittest.TestCase):
    def test0(self):
        """chi-square 1-way"""
        R="""\
Chi-Square: Single Factor

SUMMARY
           A   B   C   D  
=========================
Observed   4   5   8   15 
Expected   8   8   8    8 

CHI-SQUARE TESTS
                     Value   df     P   
=======================================
Pearson Chi-Square   9.250    3   0.026 
Likelihood Ratio     8.613    3   0.035 
Observations            32              

POST-HOC POWER
       Measure                
=============================
Effect size w           0.538 
Non-centrality lambda   9.250 
Critical Chi-Square     7.815 
Power                   0.724 """

        D=ChiSquare1way()
        D.run([4,5,8,15])
        self.assertEqual(str(D),R)

    def test1(self):
        R="ChiSquare1way([('chisq', 9.25), ('p', 0.026145200026967786), ('df', 3), ('lnchisq', 8.613046045734304), ('lnp', 0.03490361434485369), ('lndf', 3)], conditions_list=['A', 'B', 'C', 'D'])"
        D=ChiSquare1way()
        D.run([4,5,8,15])
        self.assertEqual(repr(D),R)
        
    def test1(self):
        R="""\
Chi-Square: Single Factor

SUMMARY
             1        2        3        4    
============================================
Observed        7       20       23        9 
Expected   14.750   14.750   14.750   14.750 

CHI-SQUARE TESTS
                     Value    df     P   
========================================
Pearson Chi-Square   12.797    3   0.005 
Likelihood Ratio     13.288    3   0.004 
Observations             59              

POST-HOC POWER
       Measure                 
==============================
Effect size w            0.466 
Non-centrality lambda   12.797 
Critical Chi-Square      7.815 
Power                    0.865 """

        df = DataFrame()
        df.read_tbl('data/chi_test.csv')
        X=df.chisquare1way('RESULT')
        self.assertEqual(str(X),R)

    def test2(self):
        R="""\
Chi-Square: Single Factor

SUMMARY
             1        2        3        4        5    
=====================================================
Observed        7       20       23        9        0 
Expected   11.800   11.800   11.800   11.800   11.800 

CHI-SQUARE TESTS
                     Value    df       P     
============================================
Pearson Chi-Square   30.746    4   3.450e-06 
Likelihood Ratio         --   --          -- 
Observations             59                  

POST-HOC POWER
       Measure                 
==============================
Effect size w            0.722 
Non-centrality lambda   30.746 
Critical Chi-Square      9.488 
Power                    0.998 """

        df = DataFrame()
        df.read_tbl('data/chi_test.csv')
        X=df.chisquare1way('RESULT',{1:11.8 ,2:11.8 ,3:11.8 ,4:11.8 ,5:11.8})
        
        self.assertEqual(str(X),R)

    def test3(self):
        """chi-square 1-way"""
        R="""\
Chi-Square: Single Factor

SUMMARY
            A     B     C     D  
================================
Observed   500   166   167   167 
Expected   250   250   250   250 

CHI-SQUARE TESTS
                      Value    df   P 
=====================================
Pearson Chi-Square   333.336    3   0 
Likelihood Ratio     287.686    3   0 
Observations            1000          

POST-HOC POWER
       Measure                  
===============================
Effect size w             0.577 
Non-centrality lambda   333.336 
Critical Chi-Square       7.815 
Power                         1 """

        D=ChiSquare1way()
        D.run(observed = [500,166,167,167],
              expected = [250,250,250,250])
        self.assertEqual(str(D),R)
            
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_chisquare1way)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
    
