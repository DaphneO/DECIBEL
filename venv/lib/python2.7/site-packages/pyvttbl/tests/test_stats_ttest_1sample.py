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

class Test_ttest1sample(unittest.TestCase):
    def test0(self):
        """1 sample ttest"""
        R=OrderedDict([('t', -17.797126310672542),
                       ('p2tail', 1.0172137120313963e-07),
                       ('p1tail', 5.086068560156982e-08),
                       ('n', 9),
                       ('df', 8),
                       ('mu', 4.555555555555555),
                       ('pop_mean', 20),
                       ('var', 6.777777777777778),
                       ('tc2tail', 2.3060059174895287),
                       ('tc1tail', 1.8595485016703606)])
        
        A=[3,4, 5,8,9, 1,2,4, 5]
        pop_mean=20
      
        D=Ttest()
        D.run(A, pop_mean=pop_mean)
        
        
        for k in R.keys():
            self.assertTrue(D[k],R[k])

    def test1(self):
        R="""\
t-Test: One Sample for means

                          SUPPRESSION 
=====================================
Sample Mean                    19.541 
Hypothesized Pop. Mean             17 
Variance                      228.326 
Observations                      384 
df                                383 
t Stat                          3.295 
alpha                           0.050 
P(T<=t) one-tail            5.384e-04 
t Critical one-tail             1.966 
P(T<=t) two-tail                0.001 
t Critical two-tail             1.649 
P(T<=t) two-tail                0.001 
Effect size d                   0.168 
delta                           3.295 
Observed power one-tail         0.950 
Observed power two-tail         0.908 """
        
        df = DataFrame()
        df.read_tbl('data/suppression~subjectXgroupXageXcycleXphase.csv')
        D=df.ttest('SUPPRESSION', pop_mean=17.)
        self.assertEqual(str(D),R)

            
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_ttest1sample)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
    
