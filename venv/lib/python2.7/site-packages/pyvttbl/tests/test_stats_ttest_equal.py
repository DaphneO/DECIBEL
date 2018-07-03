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

class Test_ttest_equal(unittest.TestCase):
    def test1(self):
        """independent equal variance ttest"""
        R=Ttest([('t', -1.712764845721259),
                 ('p2tail', 0.10493320627442616),
                 ('p1tail', 0.05246660313721308),
                 ('n1', 9),
                 ('n2', 10),
                 ('df', 17),
                 ('mu1', 4.555555555555555),
                 ('mu2', 9.0),
                 ('var1', 6.777777777777777),
                 ('var2', 54.22222222222222),
                 ('vpooled', 31.895424836601304),
                 ('tc2tail', 1.7396067260750672),
                 ('tc1tail', 2.1098155778331806),
                 ('cohen_d', 0.8047621870446092),
                 ('delta', 1.6095243740892184),
                 ('power1tail', 0.46028261750215127),
                 ('power2tail', 0.32962069261917515)],
                aname='A', bname='B',
                type='t-Test: Two-Sample Assuming Equal Variances')

        A=[3,4, 5,8,9, 1,2,4, 5]
        B=[6,19,3,2,14,4,5,17,1,19]
      
        D=Ttest()
        D.run(A,B,equal_variance=True)

        for k in R.keys():
            self.assertTrue(D[k],R[k])

    def test11(self):
        """independent equal variance ttest"""
        R="""\
t-Test: Two-Sample Assuming Equal Variances
                            A        B    
=========================================
Mean                       4.556        9 
Variance                   6.778   54.222 
Observations                   9       10 
Pooled Variance           31.895          
df                            17          
t Stat                    -1.713          
alpha                      0.050          
P(T<=t) one-tail           0.052          
t Critical one-tail        2.110          
P(T<=t) two-tail           0.105          
t Critical two-tail        1.740          
P(T<=t) two-tail           0.105          
Effect size d              0.805          
delta                      1.610          
Observed power one-tail    0.460          
Observed power two-tail    0.330          """
        
        A=[3,4, 5,8,9, 1,2,4, 5]
        B=[6,19,3,2,14,4,5,17,1,19]

      
        D=Ttest()
        D.run(A,B,equal_variance=True)

        self.assertEqual(str(D),R)

            
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_ttest_equal)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
    
