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

class Test_anova1way(unittest.TestCase):
    def test0(self):
        """1 way anova"""
        R=Anova1way([('f', 16.70726997413529),
                     ('p', 4.5885798225758395e-06),
                     ('ns', [14, 15, 16]),
                     ('mus', [62.142857142857146, 57.2, 94.375]),
                     ('vars', [202.13186813186815, 584.7428571428571, 339.5833333333333]),
                     ('ssbn', 12656.046825396828),
                     ('sswn', 15907.864285714284),
                     ('dfbn', 2),
                     ('dfwn', 42),
                     ('msbn', 6328.023412698414),
                     ('mswn', 378.7586734693877),
                     ('eta2', 0.4430782176910548),
                     ('lambda', 19.938519796097456),
                     ('power', 0.97789325536594729),
                     ('o_f', 4.065448310574059),
                     ('o_p', 0.02432317027325804),
                     ('o_ns', [14, 15, 16]),
                     ('o_mus', [202.1318681318681, 584.7428571428571, 339.58333333333326]),
                     ('o_vars', [29343.831505443934, 296942.8951653527, 75450.48599697657]),
                     ('o_ssbn', 1097753.8302903734),
                     ('o_sswn', 5670427.631840358),
                     ('o_dfbn', 2),
                     ('o_dfwn', 42),
                     ('o_msbn', 548876.9151451867),
                     ('o_mswn', 135010.1817104847),
                     ('o_eta2', 0.16219332126842578),
                     ('o_lambda', 7.2986994570791506),
                     ('o_power', 0.64138945570230277)],
                    multtest={('B', 'C'): {'q_df': 42,
                                           'q_crit01': 4.3543205404068921,
                                           'q_crit10': 2.9836166391724004,
                                           'q_k': 3,
                                           'q_crit05': 3.4356970960072437,
                                           'q': 3.3084936933598734,
                                           'sig': '+',
                                           'abs_diff': 37.175},
                              ('A', 'A'): {'q_df': 42,
                                           'q_crit01': 4.3543205404068921,
                                           'q_crit10': 2.9836166391724004,
                                           'q_k': 3,
                                           'q_crit05': 3.4356970960072437,
                                           'q': 0.0,
                                           'sig': 'ns',
                                           'abs_diff': 0.0},
                              ('B', 'B'): {'q_df': 42,
                                           'q_crit01': 4.3543205404068921,
                                           'q_crit10': 2.9836166391724004,
                                           'q_k': 3,
                                           'q_crit05': 3.4356970960072437,
                                           'q': 0.0,
                                           'sig': 'ns',
                                           'abs_diff': 0.0},
                              ('C', 'C'): {'q_df': 42,
                                           'q_crit01': 4.3543205404068921,
                                           'q_crit10': 2.9836166391724004,
                                           'q_k': 3,
                                           'q_crit05': 3.4356970960072437,
                                           'q': 0.0,
                                           'sig': 'ns',
                                           'abs_diff': 0.0},
                              ('A', 'B'): {'q_df': 42,
                                           'q_crit01': 4.3543205404068921,
                                           'q_crit10': 2.9836166391724004,
                                           'q_k': 3,
                                           'q_crit05': 3.4356970960072437,
                                           'q': 0.43990347503218996,
                                           'sig': 'ns',
                                           'abs_diff': 4.942857142857143},
                              ('A', 'C'): {'q_df': 42,
                                           'q_crit01': 4.3543205404068921,
                                           'q_crit10': 2.9836166391724004,
                                           'q_k': 3,
                                           'q_crit05': 3.4356970960072437,
                                           'q': 2.8685902183276837,
                                           'sig': 'ns',
                                           'abs_diff': 32.232142857142854}},
                    conditions_list=['A', 'B', 'C'])
        
        listOflists=[[42,52,55,59,75,40,79,79,44,56,68,77,75,69],
                     [29,36,29,31,97,88,27,57,54,77,54,52,58,91,78],
                     [91,79,73,75,99,66,114,120,102,68,114,79,115,104,107,104]]

        D=Anova1way()
        D.run(listOflists)                

        for key in R.keys():
            self.assertAlmostEqual(D[key],R[key])

    def test1(self):
        """1 way anova"""

        R="""Anova: Single Factor on Measure

SUMMARY
Groups   Count   Sum    Average   Variance 
==========================================
A           14    870    62.143    202.132 
B           15    858    57.200    584.743 
C           16   1510    94.375    339.583 

O'BRIEN TEST FOR HOMOGENEITY OF VARIANCE
Source of Variation       SS        df       MS         F     P-value   eta^2   Obs. power 
==========================================================================================
Treatments            1097753.830    2   548876.915   4.065     0.024   0.162        0.641 
Error                 5670427.632   42   135010.182                                        
==========================================================================================
Total                 6768181.462   44                                                     

ANOVA
Source of Variation      SS       df      MS        F       P-value    eta^2   Obs. power 
=========================================================================================
Treatments            12656.047    2   6328.023   16.707   4.589e-06   0.443        0.978 
Error                 15907.864   42    378.759                                           
=========================================================================================
Total                 28563.911   44                                                      

POSTHOC MULTIPLE COMPARISONS

Tukey HSD: Table of q-statistics
    A      B          C     
===========================
A   0   0.950 ns   6.197 ** 
B       0          7.147 ** 
C                  0        
===========================
  + p < .10 (q-critical[3, 42] = 2.98361663917)
  * p < .05 (q-critical[3, 42] = 3.43569709601)
 ** p < .01 (q-critical[3, 42] = 4.35432054041)"""
        
        listOflists=[[42,52,55,59,75,40,79,79,44,56,68,77,75,69],
                     [29,36,29,31,97,88,27,57,54,77,54,52,58,91,78],
                     [91,79,73,75,99,66,114,120,102,68,114,79,115,104,107,104]]

        D=Anova1way()
        D.run(listOflists)
        self.assertEqual(str(D),R)
        
    def test11(self):
        """1 way anova"""

        R="""Anova: Single Factor on Measure

SUMMARY
Groups   Count   Sum    Average   Variance 
==========================================
A           14    870    62.143    202.132 
B           15    858    57.200    584.743 
C           16   1510    94.375    339.583 

O'BRIEN TEST FOR HOMOGENEITY OF VARIANCE
Source of Variation       SS        df       MS         F     P-value   eta^2   Obs. power 
==========================================================================================
Treatments            1097753.830    2   548876.915   4.065     0.024   0.162        0.641 
Error                 5670427.632   42   135010.182                                        
==========================================================================================
Total                 6768181.462   44                                                     

ANOVA
Source of Variation      SS       df      MS        F       P-value    eta^2   Obs. power 
=========================================================================================
Treatments            12656.047    2   6328.023   16.707   4.589e-06   0.443        0.978 
Error                 15907.864   42    378.759                                           
=========================================================================================
Total                 28563.911   44                                                      

POSTHOC MULTIPLE COMPARISONS

SNK: Step-down table of q-statistics
 Pair     i   |diff|     q     range   df       p       Sig. 
============================================================
B vs. C   1   37.175   7.147       3   42   1.000e-03   **   
A vs. C   2   32.232   6.197       2   42   1.000e-03   **   
A vs. B   3    4.943       -       -    -           -   **   
  + p < .10,   * p < .05,   ** p < .01,   *** p < .001"""
        
        listOflists=[[42,52,55,59,75,40,79,79,44,56,68,77,75,69],
                     [29,36,29,31,97,88,27,57,54,77,54,52,58,91,78],
                     [91,79,73,75,99,66,114,120,102,68,114,79,115,104,107,104]]

        D=Anova1way()
        D.run(listOflists, posthoc='snk')

        self.assertEqual(str(D),R)

    def test2(self):
        R="""Anova: Single Factor on SUPPRESSION

SUMMARY
Groups   Count     Sum      Average   Variance 
==============================================
AA         128       2048        16    148.792 
AB         128   2510.600    19.614    250.326 
LAB        128   2945.000    23.008    264.699 

O'BRIEN TEST FOR HOMOGENEITY OF VARIANCE
Source of Variation        SS        df        MS         F     P-value   eta^2   Obs. power 
============================================================================================
Treatments             1021873.960     2   510936.980   5.229     0.006   0.027        0.823 
Error                 37227154.824   381    97709.068                                        
============================================================================================
Total                 38249028.783   383                                                     

ANOVA
Source of Variation      SS       df       MS        F      P-value    eta^2   Obs. power 
=========================================================================================
Treatments             3144.039     2   1572.020   7.104   9.348e-04   0.036        0.922 
Error                 84304.687   381    221.272                                          
=========================================================================================
Total                 87448.726   383                                                     

POSTHOC MULTIPLE COMPARISONS

Tukey HSD: Table of q-statistics
      AA      AB        LAB    
==============================
AA    0    2.749 ns   5.330 ** 
AB         0          2.581 ns 
LAB                   0        
==============================
  + p < .10 (q-critical[3, 381] = 2.91125483514)
  * p < .05 (q-critical[3, 381] = 3.32766157576)
 ** p < .01 (q-critical[3, 381] = 4.14515568451)"""
        
        df = DataFrame()
        df.read_tbl('data/suppression~subjectXgroupXageXcycleXphase.csv')
        D=df.anova1way('SUPPRESSION', 'GROUP')
        
        self.assertEqual(str(D),R)

    def test3(self):
        R = """Anova: Single Factor on Measure

SUMMARY
Groups   Count     Sum     Average   Variance 
=============================================
A           10   431.400    43.140      9.000 
B           10   894.400    89.440      4.920 
C           10   679.500    67.950      4.703 
D           10   404.700    40.470      5.936 

O'BRIEN TEST FOR HOMOGENEITY OF VARIANCE
Source of Variation      SS      df     MS       F     P-value   eta^2   Obs. power 
===================================================================================
Treatments             117.768    3   39.256   0.601     0.619   0.048        0.170 
Error                 2351.332   36   65.315                                        
===================================================================================
Total                 2469.100   39                                                 

ANOVA
Source of Variation      SS       df      MS         F       P-value    eta^2   Obs. power 
==========================================================================================
Treatments            15953.466    3   5317.822   866.118   1.341e-33   0.986        1.000 
Error                   221.034   36      6.140                                            
==========================================================================================
Total                 16174.500   39                                                       

POSTHOC MULTIPLE COMPARISONS

Tukey HSD: Table of q-statistics
    A       B           C           D     
=========================================
A   0   59.088 **   31.663 **   3.407 +   
B       0           27.426 **   62.496 ** 
C                   0           35.070 ** 
D                               0         
=========================================
  + p < .10 (q-critical[4, 36] = 3.36095129998)
  * p < .05 (q-critical[4, 36] = 3.8088367871)
 ** p < .01 (q-critical[4, 36] = 4.72966194222)"""
        
        # self data: seems incorrect q_obs
        d = [[43.9,39,46.7,43.8,44.2,47.7,43.6,38.9,43.6,40],\
             [89.8,87.1,92.7,90.6,87.7,92.4,86.1,88.1,90.8,89.1],\
             [68.4,69.3,68.5,66.4,70,68.1,70.6,65.2,63.8,69.2],\
             [36.2,45.2,40.7,40.5,39.3,40.3,43.2,38.7,40.9,39.7]]
        conditions_list = 'A B C D'.split()


        D = Anova1way()
        D.run(d, conditions_list=conditions_list)        
        self.assertEqual(str(D),R)

def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_anova1way)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
    
