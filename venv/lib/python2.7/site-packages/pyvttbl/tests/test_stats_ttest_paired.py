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

class Test_ttest_paired(unittest.TestCase):
    def test0(self):
        """paired ttest"""
        R=Ttest([('t', -1.4106912317171967),
                 ('p2tail', 0.19601578492449323),
                 ('p1tail', 0.09800789246224662),
                 ('n1', 9),
                 ('n2', 9),
                 ('r', 0.10182008678393427),
                 ('df', 8),
                 ('mu1', 4.555555555555555),
                 ('mu2', 7.888888888888889),
                 ('var1', 6.777777777777778),
                 ('var2', 47.111111111111114),
                 ('tc2tail', 1.8595480375228424),
                 ('tc1tail', 2.3060041350333704),
                 ('cohen_d', 0.47023041057239895),
                 ('delta', 1.410691231717197),
                 ('power1tail', 0.36186192660269623),
                 ('power2tail', 0.23741605057147952)],
                paired=True,
                aname='A', bname='B',
                type='t-Test: Paired Two Sample for means')
        
        A=[3,4, 5,8,9, 1,2,4, 5]
        B=[6,19,3,2,14,4,5,17,1]
      
        D=Ttest()
        D.run(A,B,paired=True)
##        print(D)
        
        for k in R.keys():
            self.assertTrue(D[k],R[k])
            
    def test01(self):
        """paired ttest"""
        R="""t-Test: Paired Two Sample for means
                            A        B    
=========================================
Mean                       4.556    7.889 
Variance                   6.778   47.111 
Observations                   9        9 
Pearson Correlation        0.102          
df                             8          
t Stat                    -1.411          
alpha                      0.050          
P(T<=t) one-tail           0.098          
t Critical one-tail        2.306          
P(T<=t) two-tail           0.196          
t Critical two-tail        1.860          
P(T<=t) two-tail           0.196          
Effect size dz             0.470          
delta                      1.411          
Observed power one-tail    0.362          
Observed power two-tail    0.237          """
        
        A=[3,4, 5,8,9, 1,2,4, 5]
        B=[6,19,3,2,14,4,5,17,1]
      
        D=Ttest()
        D.run(A,B,paired=True)


        self.assertEqual(str(D),R)

    def test4(self):
        R="""t-Test: Paired Two Sample for means
                            PRE        POST   
=============================================
Mean                        87.250     87.083 
Variance                  1207.659   1166.629 
Observations                    12         12 
Pearson Correlation          0.995            
df                              11            
t Stat                       0.163            
alpha                        0.050            
P(T<=t) one-tail             0.437            
t Critical one-tail          2.201            
P(T<=t) two-tail             0.873            
t Critical two-tail          1.796            
P(T<=t) two-tail             0.873            
Effect size dz               0.047            
delta                        0.163            
Observed power one-tail      0.068            
Observed power two-tail      0.035            """
        df = DataFrame()
        df.read_tbl('data/example2_prepost.csv')
        D = df.ttest('PRE','POST',paired=True)
        self.assertEqual(str(D),R)
        
    def test__repr__(self):
        R=Ttest([('t', 2.310889197854228), ('p2tail', 0.026382412254338405), ('p1tail', 0.013191206127169203), ('n1', 21), ('n2', 23), ('df', 37.855400659439084), ('mu1', 51.476190476190474), ('mu2', 41.52173913043478), ('var1', 121.16190476190475), ('var2', 294.0790513833993), ('tc2tail', 1.6861153650443554), ('tc1tail', 2.0246481352107009), ('cohen_d', 0.6908475708680588), ('delta', 2.1846518399376538), ('power1tail', 0.6916337616595899), ('power2tail', 0.56712772561445368)], equal_variance=False, aname='A', bname='B', type='t-Test: Two-Sample Assuming Unequal Variances')
        
        A=[24,61,59,46,43,44,52,43,58,67,62,57,71,49,54,43,53,57,49,56,33]
        B=[42,33,46,37,43,41,10,42,55,19,17,55,26,54,60,28,62,20,53,48,37,85,42]
        
        D=Ttest()
        D.run(A,B,equal_variance=False)

        for key in R.keys():
            self.assertAlmostEqual(D[key],R[key])
        


            
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_ttest_paired)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
    
