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

class Test_anova_between(unittest.TestCase):
    def test2(self):
        ## Between-Subjects test

        R = """WORDS ~ AGE * CONDITION

TESTS OF BETWEEN-SUBJECTS EFFECTS

Measure: WORDS
    Source        Type III   df     MS        F        Sig.      et2_G   Obs.    SE     95% CI   lambda   Obs.  
                     SS                                                                                   Power 
===============================================================================================================
AGE                240.250    1   240.250   29.936   3.981e-07   0.250     50   0.406    0.796   16.631   0.981 
CONDITION         1514.940    4   378.735   47.191   2.530e-21   0.677     20   0.642    1.258   41.948   1.000 
AGE * CONDITION    190.300    4    47.575    5.928   2.793e-04   0.209     10   0.908    1.780    2.635   0.207 
Error              722.300   90     8.026                                                                       
===============================================================================================================
Total             2667.790   99                                                                                 

TABLES OF ESTIMATED MARGINAL MEANS

Estimated Marginal Means for AGE
 AGE     Mean    Std. Error   95% Lower Bound   95% Upper Bound 
===============================================================
old     10.060        0.567             8.949            11.171 
young   13.160        0.818            11.556            14.764 

Estimated Marginal Means for CONDITION
CONDITION    Mean    Std. Error   95% Lower Bound   95% Upper Bound 
===================================================================
adjective   12.900        0.791            11.350            14.450 
counting     6.750        0.362             6.041             7.459 
imagery     15.500        0.933            13.671            17.329 
intention   15.650        1.096            13.502            17.798 
rhyming      7.250        0.452             6.363             8.137 

Estimated Marginal Means for AGE * CONDITION
 AGE    CONDITION    Mean    Std. Error   95% Lower Bound   95% Upper Bound 
===========================================================================
old     adjective       11        0.789             9.454            12.546 
old     counting         7        0.577             5.868             8.132 
old     imagery     13.400        1.424            10.610            16.190 
old     intention       12        1.183             9.681            14.319 
old     rhyming      6.900        0.674             5.579             8.221 
young   adjective   14.800        1.104            12.637            16.963 
young   counting     6.500        0.453             5.611             7.389 
young   imagery     17.600        0.819            15.994            19.206 
young   intention   19.300        0.844            17.646            20.954 
young   rhyming      7.600        0.618             6.388             8.812 

"""
        df=DataFrame()
        fname='data/words~ageXcondition.csv'
        df.read_tbl(fname)
        aov=Anova()
        aov.run(df,'WORDS',bfactors=['AGE','CONDITION'])
        self.assertEqual(str(aov),R)

            
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_anova_between)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
    
