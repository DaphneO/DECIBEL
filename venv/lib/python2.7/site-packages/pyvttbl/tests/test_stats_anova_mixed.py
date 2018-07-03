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

class Test_anova_mixed(unittest.TestCase):
    def test3(self):
        ## Mixed Between/Within test

        R = """\
SUPPRESSION ~ CYCLE * PHASE * GROUP

TESTS OF BETWEEN-SUBJECTS EFFECTS

Measure: SUPPRESSION
     Source        Type III   df    MS       F     Sig.    et2_G   Obs.    SE     95% CI   lambda   Obs.  
                      SS                                                                            Power 
=========================================================================================================
Between Subjects      2.034   23                                                                          
GROUP                 0.462    2   0.231   3.083   0.067   0.150      8   0.103    0.201    2.349   0.229 
=========================================================================================================
Error                 1.572   21   0.075                                                                  

TESTS OF WITHIN SUBJECTS EFFECTS

Measure: SUPPRESSION
       Source                                Type III    eps      df      MS        F        Sig.      et2_G   Obs.    SE     95% CI   lambda    Obs.  
                                                SS                                                                                               Power 
======================================================================================================================================================
CYCLE                   Sphericity Assumed      0.273       -        3   0.091    12.027   2.535e-06   0.094     48   0.013    0.025    27.491   0.995 
                        Greenhouse-Geisser      0.273   0.668    2.005   0.136    12.027   7.281e-05   0.094     48   0.013    0.025    27.491   0.967 
                        Huynh-Feldt             0.273   0.668    2.005   0.136    12.027   7.281e-05   0.094     48   0.013    0.025    27.491   0.967 
                        Box                     0.273   0.333        1   0.273    12.027       0.002   0.094     48   0.013    0.025    27.491   0.823 
------------------------------------------------------------------------------------------------------------------------------------------------------
CYCLE * GROUP           Sphericity Assumed      0.105       -        6   0.017     2.309       0.044   0.038     16   0.022    0.043     3.519   0.218 
                        Greenhouse-Geisser      0.105   0.572    3.434   0.030     2.309       0.085   0.038     16   0.022    0.043     3.519   0.167 
                        Huynh-Feldt             0.105   0.572    3.434   0.030     2.309       0.085   0.038     16   0.022    0.043     3.519   0.167 
                        Box                     0.105   0.167        1   0.105     2.309       0.158   0.038     16   0.022    0.043     3.519   0.107 
------------------------------------------------------------------------------------------------------------------------------------------------------
Error(CYCLE)            Sphericity Assumed      0.476       -       63   0.008                                                                         
                        Greenhouse-Geisser      0.476   0.572   36.061   0.013                                                                         
                        Huynh-Feldt             0.476   0.572   36.061   0.013                                                                         
                        Box                     0.476   0.167   10.500   0.045                                                                         
------------------------------------------------------------------------------------------------------------------------------------------------------
PHASE                   Sphericity Assumed      1.170       -        1   1.170   129.855   1.878e-10   0.308     96   0.010    0.020   593.625       1 
                        Greenhouse-Geisser      1.170       1        1   1.170   129.855   1.878e-10   0.308     96   0.010    0.020   593.625       1 
                        Huynh-Feldt             1.170       1        1   1.170   129.855   1.878e-10   0.308     96   0.010    0.020   593.625       1 
                        Box                     1.170       1        1   1.170   129.855   1.878e-10   0.308     96   0.010    0.020   593.625       1 
------------------------------------------------------------------------------------------------------------------------------------------------------
PHASE * GROUP           Sphericity Assumed      0.405       -        2   0.203    22.493   6.012e-06   0.134     32   0.018    0.035    68.551   1.000 
                        Greenhouse-Geisser      0.405   0.820    1.641   0.247    22.493   3.263e-05   0.134     32   0.018    0.035    68.551   1.000 
                        Huynh-Feldt             0.405   0.820    1.641   0.247    22.493   3.263e-05   0.134     32   0.018    0.035    68.551   1.000 
                        Box                     0.405   0.500        1   0.405    22.493   6.896e-04   0.134     32   0.018    0.035    68.551   1.000 
------------------------------------------------------------------------------------------------------------------------------------------------------
Error(PHASE)            Sphericity Assumed      0.189       -       21   0.009                                                                         
                        Greenhouse-Geisser      0.189   0.820   17.228   0.011                                                                         
                        Huynh-Feldt             0.189   0.820   17.228   0.011                                                                         
                        Box                     0.189   0.500   10.500   0.018                                                                         
------------------------------------------------------------------------------------------------------------------------------------------------------
CYCLE *                 Sphericity Assumed      0.074       -        3   0.025     4.035       0.011   0.027     24   0.016    0.032     4.612   0.386 
PHASE                   Greenhouse-Geisser      0.074   0.686    2.057   0.036     4.035       0.024   0.027     24   0.016    0.032     4.612   0.313 
                        Huynh-Feldt             0.074   0.686    2.057   0.036     4.035       0.024   0.027     24   0.016    0.032     4.612   0.313 
                        Box                     0.074   0.333        1   0.074     4.035       0.058   0.027     24   0.016    0.032     4.612   0.220 
------------------------------------------------------------------------------------------------------------------------------------------------------
CYCLE * PHASE * GROUP   Sphericity Assumed      0.127       -        6   0.021     3.466       0.005   0.046      8   0.028    0.055     2.641   0.169 
                        Greenhouse-Geisser      0.127   0.605    3.629   0.035     3.466       0.019   0.046      8   0.028    0.055     2.641   0.137 
                        Huynh-Feldt             0.127       1        6   0.021     3.466       0.005   0.046      8   0.028    0.055     2.641   0.169 
                        Box                     0.127   0.167        1   0.127     3.466       0.091   0.046      8   0.028    0.055     2.641   0.093 
------------------------------------------------------------------------------------------------------------------------------------------------------
Error(CYCLE *           Sphericity Assumed      0.386       -       63   0.006                                                                         
PHASE)                  Greenhouse-Geisser      0.386   0.605   38.105   0.010                                                                         
                        Huynh-Feldt             0.386       1       63   0.006                                                                         
                        Box                     0.386   0.167   10.500   0.037                                                                         

TABLES OF ESTIMATED MARGINAL MEANS

Estimated Marginal Means for CYCLE
CYCLE   Mean    Std. Error   95% Lower Bound   95% Upper Bound 
==============================================================
1       0.220        0.022             0.177             0.262 
2       0.306        0.022             0.263             0.349 
3       0.307        0.024             0.259             0.354 
4       0.308        0.026             0.257             0.359 

Estimated Marginal Means for PHASE
PHASE   Mean    Std. Error   95% Lower Bound   95% Upper Bound 
==============================================================
I       0.207        0.014             0.180             0.234 
II      0.363        0.016             0.332             0.394 

Estimated Marginal Means for GROUP
GROUP   Mean    Std. Error   95% Lower Bound   95% Upper Bound 
==============================================================
AA      0.222        0.018             0.187             0.256 
AB      0.292        0.022             0.250             0.334 
LAB     0.341        0.020             0.302             0.381 

Estimated Marginal Means for CYCLE * PHASE
CYCLE   PHASE   Mean    Std. Error   95% Lower Bound   95% Upper Bound 
======================================================================
1       I       0.173        0.028             0.119             0.228 
1       II      0.266        0.031             0.206             0.326 
2       I       0.224        0.026             0.173             0.275 
2       II      0.387        0.027             0.335             0.439 
3       I       0.223        0.027             0.170             0.276 
3       II      0.391        0.032             0.327             0.454 
4       I       0.207        0.031             0.146             0.269 
4       II      0.408        0.030             0.350             0.466 

Estimated Marginal Means for CYCLE * GROUP
CYCLE   GROUP   Mean    Std. Error   95% Lower Bound   95% Upper Bound 
======================================================================
1       AA      0.193        0.046             0.104             0.282 
1       AB      0.177        0.025             0.128             0.225 
1       LAB     0.289        0.035             0.221             0.358 
2       AA      0.253        0.033             0.187             0.318 
2       AB      0.323        0.035             0.254             0.392 
2       LAB     0.341        0.044             0.256             0.427 
3       AA      0.219        0.036             0.149             0.289 
3       AB      0.331        0.039             0.255             0.406 
3       LAB     0.371        0.044             0.285             0.456 
4       AA      0.223        0.026             0.172             0.273 
4       AB      0.337        0.057             0.225             0.449 
4       LAB     0.364        0.040             0.287             0.442 

Estimated Marginal Means for PHASE * GROUP
PHASE   GROUP   Mean    Std. Error   95% Lower Bound   95% Upper Bound 
======================================================================
I       AA      0.209        0.024             0.162             0.255 
I       AB      0.179        0.023             0.134             0.225 
I       LAB     0.233        0.026             0.183             0.283 
II      AA      0.235        0.026             0.184             0.286 
II      AB      0.404        0.023             0.359             0.450 
II      LAB     0.450        0.016             0.419             0.481 

Estimated Marginal Means for CYCLE * PHASE * GROUP
CYCLE   PHASE   GROUP   Mean    Std. Error   95% Lower Bound   95% Upper Bound 
==============================================================================
1       I       AA      0.177        0.060             0.060             0.295 
1       I       AB      0.126        0.036             0.056             0.196 
1       I       LAB     0.216        0.047             0.124             0.309 
1       II      AA      0.209        0.072             0.067             0.351 
1       II      AB      0.228        0.025             0.179             0.276 
1       II      LAB     0.363        0.038             0.288             0.437 
2       I       AA      0.224        0.039             0.148             0.300 
2       I       AB      0.235        0.049             0.139             0.331 
2       I       LAB     0.214        0.053             0.110             0.317 
2       II      AA      0.281        0.055             0.173             0.389 
2       II      AB      0.411        0.026             0.360             0.463 
2       II      LAB     0.469        0.026             0.417             0.520 
3       I       AA      0.231        0.057             0.120             0.342 
3       I       AB      0.200        0.031             0.140             0.260 
3       I       LAB     0.238        0.054             0.133             0.342 
3       II      AA      0.208        0.047             0.115             0.300 
3       II      AB      0.461        0.024             0.414             0.508 
3       II      LAB     0.504        0.016             0.472             0.535 
4       I       AA      0.203        0.039             0.126             0.279 
4       I       AB      0.156        0.062             0.036             0.277 
4       I       LAB     0.264        0.058             0.149             0.378 
4       II      AA      0.242        0.034             0.176             0.309 
4       II      AB      0.517        0.031             0.457             0.578 
4       II      LAB     0.465        0.020             0.425             0.505 

"""
        df=DataFrame()
        fname='data/suppression~subjectXgroupXcycleXphase.csv'
        df.read_tbl(fname)
        df['SUPPRESSION']=[.01*x for x in df['SUPPRESSION']]
        aov=df.anova('SUPPRESSION',wfactors=['CYCLE','PHASE'],bfactors=['GROUP'])
##        print(aov)
        self.assertEqual(str(aov),R)


            
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_anova_mixed)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
    
