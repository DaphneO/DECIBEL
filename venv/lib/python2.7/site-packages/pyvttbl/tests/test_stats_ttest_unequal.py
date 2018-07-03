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

class Test_ttest_unequal(unittest.TestCase):
    def test2(self):
        """independent unequal variance ttest"""
        R=Ttest([('t', -1.7884967184189302),
                 ('p2tail', 0.1002162848567985),
                 ('p1tail', 0.05010814242839925),
                 ('n1', 9),
                 ('n2', 10),
                 ('df', 11.425658453695835),
                 ('mu1', 4.555555555555555),
                 ('mu2', 9.0),
                 ('var1', 6.777777777777777),
                 ('var2', 54.22222222222222),
                 ('tc2tail', 1.789781988406649),
                 ('tc1tail', 2.1910222595585718),
                 ('cohen_d', 0.8047621870446092),
                 ('delta', 1.6095243740892184),
                 ('power1tail', 0.44778738859279099),
                 ('power2tail', 0.31400143046586182)],
                equal_variance=False,
                aname='A', bname='B',
                type='t-Test: Two-Sample Assuming Unequal Variances')
        
        A=[3,4, 5,8,9, 1,2,4, 5]
        B=[6,19,3,2,14,4,5,17,1,19]
      
        D=Ttest()
        D.run(A,B,equal_variance=False)

        for k in R.keys():
            self.assertTrue(D[k],R[k])

    def test21(self):
        """independent unequal variance ttest"""
        R="""t-Test: Two-Sample Assuming Unequal Variances
                            A        B    
=========================================
Mean                       4.556        9 
Variance                   6.778   54.222 
Observations                   9       10 
df                        11.426          
t Stat                    -1.788          
alpha                      0.050          
P(T<=t) one-tail           0.050          
t Critical one-tail        2.191          
P(T<=t) two-tail           0.100          
t Critical two-tail        1.790          
P(T<=t) two-tail           0.100          
Effect size d              0.805          
delta                      1.610          
Observed power one-tail    0.448          
Observed power two-tail    0.314          """
        
        A=[3,4, 5,8,9, 1,2,4, 5]
        B=[6,19,3,2,14,4,5,17,1,19]
      
        D=Ttest()
        D.run(A,B,equal_variance=False)

        self.assertEqual(str(D),R)
        
    def test3(self):
        """independent unequal variance ttest
        http://alamos.math.arizona.edu/~rychlik/math263/class_notes/Chapter7/R/"""
        R=Ttest([('t', 2.310889197854228),
                 ('p2tail', 0.026382412254338405),
                 ('p1tail', 0.013191206127169203),
                 ('n1', 21),
                 ('n2', 23),
                 ('df', 37.855400659439084),
                 ('mu1', 51.476190476190474),
                 ('mu2', 41.52173913043478),
                 ('var1', 121.16190476190475),
                 ('var2', 294.0790513833993),
                 ('tc2tail', 1.6861153650443554),
                 ('tc1tail', 2.0246481352107009),
                 ('cohen_d', 0.6908475708680588),
                 ('delta', 2.1846518399376538),
                 ('power1tail', 0.6916337616595899),
                 ('power2tail', 0.56712772561445368)],
                equal_variance=False,
                aname='A', bname='B',
                type='t-Test: Two-Sample Assuming Unequal Variances')
        
        A=[24,61,59,46,43,44,52,43,58,67,62,57,71,49,54,43,53,57,49,56,33]
        B=[42,33,46,37,43,41,10,42,55,19,17,55,26,54,60,28,62,20,53,48,37,85,42]
      
        D=Ttest()
        D.run(A,B,equal_variance=False)


        for k in R.keys():
            self.assertTrue(D[k],R[k])

    def test31(self):
        """independent unequal variance ttest
        http://alamos.math.arizona.edu/~rychlik/math263/class_notes/Chapter7/R/"""
        R="""\
t-Test: Two-Sample Assuming Unequal Variances
                             A         B    
===========================================
Mean                       51.476    41.522 
Variance                  121.162   294.079 
Observations                   21        23 
df                         37.855           
t Stat                      2.311           
alpha                       0.050           
P(T<=t) one-tail            0.013           
t Critical one-tail         2.025           
P(T<=t) two-tail            0.026           
t Critical two-tail         1.686           
P(T<=t) two-tail            0.026           
Effect size d               0.691           
delta                       2.185           
Observed power one-tail     0.692           
Observed power two-tail     0.567           """
        
        A=[24,61,59,46,43,44,52,43,58,67,62,57,71,49,54,43,53,57,49,56,33]
        B=[42,33,46,37,43,41,10,42,55,19,17,55,26,54,60,28,62,20,53,48,37,85,42]
      
        D=Ttest()
        D.run(A,B,equal_variance=False)

        self.assertEqual(str(D),R)

        

            
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_ttest_unequal)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
    
