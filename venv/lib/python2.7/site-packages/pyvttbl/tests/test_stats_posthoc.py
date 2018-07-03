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

class Test_posthoc(unittest.TestCase):
    def test31(self):
        """1 way anova"""

        R="""Anova: Single Factor on Measure

SUMMARY
Groups    Count   Sum   Average   Variance 
==========================================
Contact      10   300        30    116.444 
Hit          10   350        35     86.444 
Bump         10   380        38    122.222 
Collide      10   410        41     41.556 
Smash        10   460        46     33.333 

O'BRIEN TEST FOR HOMOGENEITY OF VARIANCE
Source of Variation       SS       df      MS         F     P-value   eta^2   Obs. power 
========================================================================================
Treatments             68081.975    4   17020.494   1.859     0.134   0.142        0.498 
Error                 412050.224   45    9156.672                                        
========================================================================================
Total                 480132.199   49                                                    

ANOVA
Source of Variation    SS    df   MS      F     P-value   eta^2   Obs. power 
============================================================================
Treatments            1460    4   365   4.562     0.004   0.289        0.837 
Error                 3600   45    80                                        
============================================================================
Total                 5060   49                                              

POSTHOC MULTIPLE COMPARISONS

SNK: Step-down table of q-statistics
       Pair           i    |diff|     q     range   df     p     Sig. 
=====================================================================
Contact vs. Smash      1   16.000   5.657       5   45   0.002   **   
Collide vs. Contact    2   11.000   3.889       4   45   0.041   *    
Hit vs. Smash          3   11.000   3.889       4   45   0.041   *    
Bump vs. Smash         4    8.000   2.828       3   45   0.124   ns   
Bump vs. Contact       5    8.000   2.828       3   45   0.124   ns   
Collide vs. Hit        6    6.000   2.121       2   45   0.141   ns   
Collide vs. Smash      7    5.000       -       -    -       -   ns   
Contact vs. Hit        8    5.000       -       -    -       -   ns   
Bump vs. Collide       9    3.000       -       -    -       -   ns   
Bump vs. Hit          10    3.000       -       -    -       -   ns   
  + p < .10,   * p < .05,   ** p < .01,   *** p < .001"""
        
        listOflists=[[21,20,26,46,35,13,41,30,42,26],
                     [23,30,34,51,20,38,34,44,41,35],
                     [35,35,52,29,54,32,30,42,50,21],
                     [44,40,33,45,45,30,46,34,49,44],
                     [39,44,51,47,50,45,39,51,39,55]]

        conditions_list = ['Contact','Hit','Bump','Collide','Smash']

        D=Anova1way()
        D.run(listOflists, conditions_list=conditions_list, posthoc='snk')
        
        self.assertEqual(str(D),R)

    def test32(self):
        """1 way anova"""

        R="""Anova: Single Factor on Measure

SUMMARY
Groups    Count   Sum   Average   Variance 
==========================================
Contact      10   300        30    116.444 
Hit          10   350        35     86.444 
Bump         10   380        38    122.222 
Collide      10   410        41     41.556 
Smash        10   460        46     33.333 

O'BRIEN TEST FOR HOMOGENEITY OF VARIANCE
Source of Variation       SS       df      MS         F     P-value   eta^2   Obs. power 
========================================================================================
Treatments             68081.975    4   17020.494   1.859     0.134   0.142        0.498 
Error                 412050.224   45    9156.672                                        
========================================================================================
Total                 480132.199   49                                                    

ANOVA
Source of Variation    SS    df   MS      F     P-value   eta^2   Obs. power 
============================================================================
Treatments            1460    4   365   4.562     0.004   0.289        0.837 
Error                 3600   45    80                                        
============================================================================
Total                 5060   49                                              

POSTHOC MULTIPLE COMPARISONS

Tukey HSD: Table of q-statistics
          Bump   Collide    Contact      Hit       Smash   
==========================================================
Bump      0      1.061 ns   2.828 ns   1.061 ns   2.828 ns 
Collide          0          3.889 +    2.121 ns   1.768 ns 
Contact                     0          1.768 ns   5.657 ** 
Hit                                    0          3.889 +  
Smash                                             0        
==========================================================
  + p < .10 (q-critical[5, 45] = 3.59038343675)
  * p < .05 (q-critical[5, 45] = 4.01861178004)
 ** p < .01 (q-critical[5, 45] = 4.89280842987)"""
        
        listOflists=[[21,20,26,46,35,13,41,30,42,26],
                     [23,30,34,51,20,38,34,44,41,35],
                     [35,35,52,29,54,32,30,42,50,21],
                     [44,40,33,45,45,30,46,34,49,44],
                     [39,44,51,47,50,45,39,51,39,55]]

        conditions_list = ['Contact','Hit','Bump','Collide','Smash']

        D=Anova1way()
        D.run(listOflists, conditions_list=conditions_list, posthoc='tukey')
        
        self.assertEqual(str(D),R)
            
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_posthoc)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
    
