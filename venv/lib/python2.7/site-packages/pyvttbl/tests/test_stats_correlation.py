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

class Test_correlation(unittest.TestCase):
    def test0(self):
        R="""Correlation([\
(('t1', 't2'), {'p': 9.699461194116956e-12, 'r': 0.9577922077922078}), \
(('t1', 't3'), {'p': 2.2594982244811486e-09, 'r': -0.924025974025974}), \
(('t2', 't3'), {'p': 6.850166042119375e-08, 'r': -0.8896103896103895})], \
conditions_list=['t1', 't2', 't3'], coefficient='spearman', N=21)"""
        
        A=[24,61,59,46,43,44,52,43,58,67,62,57,71,49,54,43,53,57,49,56,33]
        B=[42.93472681237495, 78.87307334936268, 75.37292628918023,
           65.49076317291956, 55.55965179772366, 56.777730638998236,
           62.19451880792437, 54.73710611356715, 72.10021832823149,
           85.94377749485642, 78.2087578930983, 72.01681829338037,
           84.27889316830063, 60.20516982367225, 65.6276497088971,
           62.36549856901088, 69.18772114281175, 67.00548667483324,
           59.042687027269466, 71.99214593063917, 45.00831155783992]
        C=[-53.05540625388731, -96.33996451998567, -92.32465861908086,
           -70.90536432779966, -55.953777697739255, -74.12814626217357,
           -75.89188834814621, -64.24093256012688, -89.62208010083313,
           -87.41075066046812, -80.40932820298143, -77.99906284144805,
           -95.31607277596169, -61.672429800914486, -85.26088499198657,
           -63.4402296673869, -74.84950736563589, -85.00433219746624,
           -71.5901436929124, -76.43243666219388, -48.01082320924727]

        cor=Correlation()
        cor.run([A,B,C],['t1','t2','t3'],coefficient='spearman')
        self.assertEqual(repr(cor),R)

    def test1(self):
        R="""\
Bivariate Correlations

                         A           B           C     
======================================================
A   spearman                 1       0.958      -0.924 
    Sig (2-tailed)           .   9.699e-12   2.259e-09 
    N                       21          21          21 
------------------------------------------------------
B   spearman             0.958           1      -0.890 
    Sig (2-tailed)   9.699e-12           .   6.850e-08 
    N                       21          21          21 
------------------------------------------------------
C   spearman            -0.924      -0.890           1 
    Sig (2-tailed)   2.259e-09   6.850e-08           . 
    N                       21          21          21 

Larzelere and Mulaik Significance Testing

 Pair     i   Correlation       P       alpha/(k-i+1)   Sig. 
============================================================
A vs. B   1         0.958   9.699e-12           0.017   **   
A vs. C   2         0.924   2.259e-09           0.025   **   
B vs. C   3         0.890   6.850e-08           0.050   **   """
        df=DataFrame()
        df['A']=[24,61,59,46,43,44,52,43,58,67,62,57,71,49,54,43,53,57,49,56,33]
        df['B']=[42.93472681237495, 78.87307334936268, 75.37292628918023,
                 65.49076317291956, 55.55965179772366, 56.777730638998236,
                 62.19451880792437, 54.73710611356715, 72.10021832823149,
                 85.94377749485642, 78.2087578930983, 72.01681829338037,
                 84.27889316830063, 60.20516982367225, 65.6276497088971,
                 62.36549856901088, 69.18772114281175, 67.00548667483324,
                 59.042687027269466, 71.99214593063917, 45.00831155783992]
        df['C']=[-53.05540625388731, -96.33996451998567, -92.32465861908086,
                 -70.90536432779966, -55.953777697739255, -74.12814626217357,
                 -75.89188834814621, -64.24093256012688, -89.62208010083313,
                 -87.41075066046812, -80.40932820298143, -77.99906284144805,
                 -95.31607277596169, -61.672429800914486, -85.26088499198657,
                 -63.4402296673869, -74.84950736563589, -85.00433219746624,
                 -71.5901436929124, -76.43243666219388, -48.01082320924727]
        
        cor=df.correlation(['A','B','C'],coefficient='spearman')
        print(cor)
        self.assertEqual(str(cor),R)

    def test2(self):
        df = DataFrame()
        df.read_tbl('data/iqbrainsize.txt', delimiter='\t')
        cor = df.correlation(df.keys())
            
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_correlation)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
    
