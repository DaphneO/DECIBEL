from __future__ import print_function

# Copyright (c) 2011, Roger Lew [see LICENSE.txt]
# This software is funded in part by NIH Grant P20 RR016454.

# Python 2 to 3 workarounds
import sys
if sys.version_info[0] == 2:
    _strobj = basestring
    _xrange = xrange
elif sys.version_info[0] == 3:
    _strobj = str
    _xrange = range
    
import unittest
import warnings
import os

import numpy as np
from pyvttbl import DataFrame
from pyvttbl.plotting import interaction_plot
from pyvttbl.misc.support import *

class Test_interaction_plot(unittest.TestCase):
    
    def test0(self):
        """no error bars specified"""
        R = {'aggregate': None,
             'clevels': [1],
             'fname': 'output\\interaction_plot(WORDS~AGE_X_CONDITION).png',
             'maintitle': 'WORDS by AGE * CONDITION',
             'numcols': 1,
             'numrows': 1,
             'rlevels': [1],
             'subplot_titles': [''],
             'xmaxs': [1.5],
             'xmins': [-0.5],
             'y': [[[11.0, 14.8],
                    [7.0, 6.5],
                    [13.4, 17.6],
                    [12.0, 19.3],
                    [6.9, 7.6]]],
             'yerr': [[]],
             'ymin': 0.0,
             'ymax': 27.183257964740832}
        
        # a simple plot
        df=DataFrame()
        df.TESTMODE=True
        df.read_tbl('data/words~ageXcondition.csv')
        D=df.interaction_plot('WORDS','AGE',
                              seplines='CONDITION',
                              output_dir='output')

        self.assertEqual(D['aggregate'],      R['aggregate'])
        self.assertEqual(D['clevels'],        R['clevels'])
        self.assertEqual(D['rlevels'],        R['rlevels'])
        self.assertEqual(D['numcols'],        R['numcols'])
        self.assertEqual(D['numrows'],        R['numrows'])
        self.assertEqual(D['fname'],          R['fname'])
        self.assertEqual(D['maintitle'],      R['maintitle'])
        self.assertEqual(D['subplot_titles'], R['subplot_titles'])
        self.assertAlmostEqual(D['ymin'],     R['ymin'])
        self.assertAlmostEqual(D['ymax'],     R['ymax'])

        for d,r in zip(np.array(D['y']).flat,
                       np.array(R['y']).flat):
            self.assertAlmostEqual(d,r)

        for d,r in zip(np.array(D['yerr']).flat,
                       np.array(R['yerr']).flat):
            self.assertAlmostEqual(d,r)
            
    def test01(self):
        """confidence interval error bars specified"""
        
        R = {'aggregate': 'ci',
             'clevels': [1],
             'fname': 'output\\interaction_plot(WORDS~AGE_X_CONDITION,yerr=95% ci).png',
             'maintitle': 'WORDS by AGE * CONDITION',
             'numcols': 1,
             'numrows': 1,
             'rlevels': [1],
             'subplot_titles': [''],
             'xmaxs': [1.5],
             'xmins': [-0.5],
             'y': [[[11.0, 14.8],
                    [7.0, 6.5],
                    [13.4, 17.6],
                    [12.0, 19.3],
                    [6.9, 7.6]]],
             'yerr': [[]],
             'ymin': 0.0,
             'ymax': 27.183257964740832}
        
        # a simple plot
        df=DataFrame()
        df.TESTMODE=True
        df.read_tbl('data/words~ageXcondition.csv')
        D=df.interaction_plot('WORDS','AGE',
                              seplines='CONDITION',
                              output_dir='output',
                              yerr='ci')

        self.assertEqual(D['aggregate'],      R['aggregate'])
        self.assertEqual(D['clevels'],        R['clevels'])
        self.assertEqual(D['rlevels'],        R['rlevels'])
        self.assertEqual(D['numcols'],        R['numcols'])
        self.assertEqual(D['numrows'],        R['numrows'])
        self.assertEqual(D['fname'],          R['fname'])
        self.assertEqual(D['maintitle'],      R['maintitle'])
        self.assertEqual(D['subplot_titles'], R['subplot_titles'])
        self.assertAlmostEqual(D['ymin'],     R['ymin'])
        self.assertAlmostEqual(D['ymax'],     R['ymax'])

        for d,r in zip(np.array(D['y']).flat,
                       np.array(R['y']).flat):
            self.assertAlmostEqual(d,r)

        for d,r in zip(np.array(D['yerr']).flat,
                       np.array(R['yerr']).flat):
            self.assertAlmostEqual(d,r)

            
    def test02(self):
        """using loftus and masson error bars"""
        
        # a simple plot
        df=DataFrame()
        df.read_tbl('data/words~ageXcondition.csv')
        aov = df.anova('WORDS', wfactors=['AGE','CONDITION'])
        aov.plot('WORDS','AGE', seplines='CONDITION',
                 errorbars='ci', output_dir='output')


    def test1(self):
        R = {'aggregate': None,
             'clevels': ['M1', 'M2', 'M3'],
             'fname': 'output\\interaction_plot(ERROR~TIMEOFDAY_X_COURSE_X_MODEL,yerr=1.0).png',
             'maintitle': 'ERROR by TIMEOFDAY * COURSE * MODEL',
             'numcols': 3,
             'numrows': 1,
             'rlevels': [1],
             'subplot_titles': ['M1', 'M2', 'M3'],
             'xmaxs': [1.5, 1.5, 1.5],
             'xmins': [-0.5, -0.5, -0.5],
             'y': [[[ 9.        ,  4.33333333],
                    [ 8.66666667,  3.66666667],
                    [ 4.66666667,  1.66666667]],
                   [[ 7.5       ,  2.66666667],
                    [ 6.        ,  2.66666667],
                    [ 5.        ,  1.66666667]],
                   [[ 5.        ,  2.66666667],
                    [ 3.5       ,  2.33333333],
                    [ 2.33333333,  1.33333333]]],
             'yerr': [[1.0, 1.0],
                      [1.0, 1.0],
                      [1.0, 1.0]],
             'ymax': 11.119188627248182,
             'ymin': 0.0}
        
        # specify yerr
        df=DataFrame()
        df.TESTMODE = True
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        D=df.interaction_plot('ERROR','TIMEOFDAY',
                              seplines='COURSE',
                              sepxplots='MODEL',
                              yerr=1.,
                              output_dir='output')   

        self.assertEqual(D['aggregate'],      R['aggregate'])
        self.assertEqual(D['clevels'],        R['clevels'])
        self.assertEqual(D['rlevels'],        R['rlevels'])
        self.assertEqual(D['numcols'],        R['numcols'])
        self.assertEqual(D['numrows'],        R['numrows'])
        self.assertEqual(D['fname'],          R['fname'])
        self.assertEqual(D['maintitle'],      R['maintitle'])
        self.assertEqual(D['subplot_titles'], R['subplot_titles'])
        self.assertAlmostEqual(D['ymin'],     R['ymin'])
        self.assertAlmostEqual(D['ymax'],     R['ymax'])

        for d,r in zip(np.array(D['y']).flat,
                       np.array(R['y']).flat):
            self.assertAlmostEqual(d,r)

        for d,r in zip(np.array(D['yerr']).flat,
                       np.array(R['yerr']).flat):
            self.assertAlmostEqual(d,r)

    def test2(self):
        R = {'aggregate': 'ci',
             'clevels': [1],
             'fname': 'output\\interaction_plot(SUPPRESSION~CYCLE_X_AGE_X_PHASE,yerr=95% ci).png',
             'maintitle': 'SUPPRESSION by CYCLE * AGE * PHASE',
             'numcols': 1,
             'numrows': 2,
             'rlevels': ['I', 'II'],
             'subplot_titles': ['I', 'II'],
             'xmaxs': [4.1749999999999998, 4.1749999999999998],
             'xmins': [0.32499999999999996, 0.32499999999999996],
             'y': [[[ 17.33333333,  22.41666667,  22.29166667,  20.75      ],
                    [  7.34166667,   9.65      ,   9.70833333,   9.10833333]],
                   [[ 26.625     ,  38.70833333,  39.08333333,  40.83333333],
                    [ 10.24166667,  12.575     ,  13.19166667,  12.79166667]]],
             'yerr': [[ 1.81325589,  1.44901936,  1.60883063,  1.57118871],
                      [ 2.49411239,  1.34873573,  1.95209851,  1.35412572]],
             'ymax': 64.8719707118471,
             'ymin': 0.0}
        
        # generate yerr
        df=DataFrame()
        df.TESTMODE = True
        df.read_tbl('data\suppression~subjectXgroupXageXcycleXphase.csv')

        D = df.interaction_plot('SUPPRESSION','CYCLE',
                                seplines='AGE',
                                sepyplots='PHASE',
                                yerr='ci',
                                output_dir='output')
        
        self.assertEqual(D['aggregate'],      R['aggregate'])
        self.assertEqual(D['clevels'],        R['clevels'])
        self.assertEqual(D['rlevels'],        R['rlevels'])
        self.assertEqual(D['numcols'],        R['numcols'])
        self.assertEqual(D['numrows'],        R['numrows'])
        self.assertEqual(D['fname'],          R['fname'])
        self.assertEqual(D['maintitle'],      R['maintitle'])
        self.assertEqual(D['subplot_titles'], R['subplot_titles'])
        self.assertAlmostEqual(D['ymin'],     R['ymin'])
        self.assertAlmostEqual(D['ymax'],     R['ymax'])
        
        for d,r in zip(np.array(D['y']).flat,np.array(R['y']).flat):
            self.assertAlmostEqual(d,r)

        for d,r in zip(np.array(D['yerr']).flat,np.array(R['yerr']).flat):
            self.assertAlmostEqual(d,r)

    def test3(self):
        R = {'aggregate': 'ci',
             'clevels': ['I', 'II'],
             'fname': 'output\\whereGROUPnotLAB.png',
             'maintitle': 'SUPPRESSION by CYCLE * AGE * PHASE * GROUP',
             'numcols': 2,
             'numrows': 2,
             'rlevels': ['AA', 'AB'],
             'subplot_titles': ['GROUP = AA, PHASE = AA',
                                'GROUP = AA, PHASE = AA',
                                'GROUP = AB, PHASE = AB',
                                'GROUP = AB, PHASE = AB'],
             'xmaxs': [4.1500000000000004,
                       4.1500000000000004,
                       4.1500000000000004,
                       4.1500000000000004],
             'xmins': [0.84999999999999998,
                       0.84999999999999998,
                       0.84999999999999998,
                       0.84999999999999998],
             'y': [[[ 17.75 ,  22.375,  23.125,  20.25 ],
                    [  8.675,  10.225,  10.5  ,   9.925]],
                   [[ 20.875,  28.125,  20.75 ,  24.25 ],
                    [  8.3  ,  10.25 ,   9.525,  11.1  ]],
                   [[ 12.625,  23.5  ,  20.   ,  15.625],
                    [  5.525,   8.825,   9.125,   7.75 ]],
                   [[ 22.75 ,  41.125,  46.125,  51.75 ],
                    [  8.675,  13.1  ,  14.475,  12.85 ]]],
             'ymax': 64.8719707118471,
             'ymin': 0.0}
                    
        # separate y plots and separate x plots
        df=DataFrame()
        df.TESTMODE = True
        df.read_tbl('data\suppression~subjectXgroupXageXcycleXphase.csv')

        D = df.interaction_plot('SUPPRESSION','CYCLE',
                                seplines='AGE',
                                sepxplots='PHASE',
                                sepyplots='GROUP',yerr='ci',
                                where=[('GROUP','not in',['LAB'])],
                                fname='whereGROUPnotLAB.png',
                                output_dir='output')

        
        self.assertEqual(D['aggregate'],      R['aggregate'])
        self.assertEqual(D['clevels'],        R['clevels'])
        self.assertEqual(D['rlevels'],        R['rlevels'])
        self.assertEqual(D['numcols'],        R['numcols'])
        self.assertEqual(D['numrows'],        R['numrows'])
        self.assertEqual(D['fname'],          R['fname'])
        self.assertEqual(D['maintitle'],      R['maintitle'])
        self.assertEqual(D['subplot_titles'], R['subplot_titles'])
        self.assertAlmostEqual(D['ymin'],     R['ymin'])
        self.assertAlmostEqual(D['ymax'],     R['ymax'])

        for d,r in zip(np.array(D['y']).flat,np.array(R['y']).flat):
            self.assertAlmostEqual(d,r)

    def test31(self):
                    
        # separate y plots and separate x plots
        df=DataFrame()
        df.TESTMODE = True
        df.read_tbl('data\suppression~subjectXgroupXageXcycleXphase.csv')

        D = df.interaction_plot('SUPPRESSION','CYCLE',
                                seplines='AGE',
                                sepxplots='GROUP',
                                sepyplots='PHASE',
                                yerr='sem',
                                output_dir='output')

    # the code for when seplines=None is in a different branch
    # these test that code
    def test4(self):
        R = {'aggregate': None,
             'clevels': ['adjective',
                         'counting',
                         'imagery',
                         'intention',
                         'rhyming'],
             'fname': 'output\\interaction_plot(WORDS~AGE_X_CONDITION).png',
             'maintitle': 'WORDS by AGE * CONDITION',
             'numcols': 5,
             'numrows': 1,
             'rlevels': [1],
             'subplot_titles': ['adjective',
                                'counting',
                                'imagery',
                                'intention',
                                'rhyming'],
             'xmaxs': [1.5, 1.5, 1.5, 1.5, 1.5],
             'xmins': [-0.5, -0.5, -0.5, -0.5, -0.5],
             'y': [[ 11. ,  14.8],
                   [  7. ,   6.5],
                   [ 13.4,  17.6],
                   [ 12. ,  19.3],
                   [  6.9,   7.6]],
             'yerr': [[], [], [], [], []],
             'ymax': 27.183257964740832,
             'ymin': 0.0}
        
        # a simple plot
        df=DataFrame()
        df.TESTMODE = True
        df.read_tbl('data/words~ageXcondition.csv')
        D = df.interaction_plot('WORDS','AGE',
                                sepxplots='CONDITION',
                                output_dir='output')
        
        self.assertEqual(D['aggregate'],      R['aggregate'])
        self.assertEqual(D['clevels'],        R['clevels'])
        self.assertEqual(D['rlevels'],        R['rlevels'])
        self.assertEqual(D['numcols'],        R['numcols'])
        self.assertEqual(D['numrows'],        R['numrows'])
        self.assertEqual(D['fname'],          R['fname'])
        self.assertEqual(D['maintitle'],      R['maintitle'])
        self.assertEqual(D['subplot_titles'], R['subplot_titles'])
        self.assertAlmostEqual(D['ymin'],     R['ymin'])
        self.assertAlmostEqual(D['ymax'],     R['ymax'])
        
        for d,r in zip(np.array(D['y']).flat,
                       np.array(R['y']).flat):
            self.assertAlmostEqual(d,r)

        for d,r in zip(np.array(D['yerr']).flat,
                       np.array(R['yerr']).flat):
            self.assertAlmostEqual(d,r)
        
    def test5(self):
        R = {'aggregate': None,
             'clevels': ['M1', 'M2', 'M3'],
             'fname': 'output\\interaction_plot(ERROR~TIMEOFDAY_X_MODEL,yerr=1.0).png',
             'maintitle': 'ERROR by TIMEOFDAY * MODEL',
             'numcols': 3,
             'numrows': 1,
             'rlevels': [1],
             'subplot_titles': ['M1', 'M2', 'M3'],
             'xmaxs': [1.5, 1.5, 1.5],
             'xmins': [-0.5, -0.5, -0.5],
             'y': [[ 7.25      ,  3.22222222],
                   [ 6.        ,  2.33333333],
                   [ 3.42857143,  2.11111111]],
             'yerr': [[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]],
             'ymax': 11.119188627248182,
             'ymin': 0.0}
                    
        # specify yerr
        df=DataFrame()
        df.TESTMODE = True
        df.read_tbl('data/error~subjectXtimeofdayXcourseXmodel_MISSING.csv')
        D = df.interaction_plot('ERROR','TIMEOFDAY',
                                sepxplots='MODEL',
                                yerr=1.,
                                output_dir='output')
        
        self.assertEqual(D['aggregate'],      R['aggregate'])
        self.assertEqual(D['clevels'],        R['clevels'])
        self.assertEqual(D['rlevels'],        R['rlevels'])
        self.assertEqual(D['numcols'],        R['numcols'])
        self.assertEqual(D['numrows'],        R['numrows'])
        self.assertEqual(D['fname'],          R['fname'])
        self.assertEqual(D['maintitle'],      R['maintitle'])
        self.assertEqual(D['subplot_titles'], R['subplot_titles'])
        self.assertAlmostEqual(D['ymin'],     R['ymin'])
        self.assertAlmostEqual(D['ymax'],     R['ymax'])
        
        for d,r in zip(np.array(D['y']).flat,
                       np.array(R['y']).flat):
            self.assertAlmostEqual(d,r)

        for d,r in zip(np.array(D['yerr']).flat,
                       np.array(R['yerr']).flat):
            self.assertAlmostEqual(d,r)
            
    def test6(self):
        R = {'aggregate': 'ci',
             'clevels': [1],
             'fname': 'output\\interaction_plot(SUPPRESSION~CYCLE_X_PHASE,yerr=95% ci).png',
             'maintitle': 'SUPPRESSION by CYCLE * PHASE',
             'numcols': 1,
             'numrows': 2,
             'rlevels': ['I', 'II'],
             'subplot_titles': ['I', 'II'],
             'xmaxs': [4.1749999999999998, 4.1749999999999998],
             'xmins': [0.82499999999999996, 0.82499999999999996],
             'y': [[ 12.3375    ,  16.03333333,  16.        ,  14.92916667],
                   [ 18.43333333,  25.64166667,  26.1375    ,  26.8125    ]],
             'yerr': [[ 3.18994762,  3.20528834,  3.26882751,  3.53477953],
                      [ 3.98429064,  4.5950803 ,  4.9514978 ,  4.97429769]],
             'ymax': 64.8719707118471,
             'ymin': 0.0}
        
        # generate yerr
        df=DataFrame()
        df.TESTMODE = True
        df.read_tbl('data\suppression~subjectXgroupXageXcycleXphase.csv')
        D = df.interaction_plot('SUPPRESSION','CYCLE',
                                sepyplots='PHASE',
                                yerr='ci',
                                output_dir='output')

        self.assertEqual(D['aggregate'],      R['aggregate'])
        self.assertEqual(D['clevels'],        R['clevels'])
        self.assertEqual(D['rlevels'],        R['rlevels'])
        self.assertEqual(D['numcols'],        R['numcols'])
        self.assertEqual(D['numrows'],        R['numrows'])
        self.assertEqual(D['fname'],          R['fname'])
        self.assertEqual(D['maintitle'],      R['maintitle'])
        self.assertEqual(D['subplot_titles'], R['subplot_titles'])
        self.assertAlmostEqual(D['ymin'],     R['ymin'])
        self.assertAlmostEqual(D['ymax'],     R['ymax'])
        
        for d,r in zip(np.array(D['y']).flat,
                       np.array(R['y']).flat):
            self.assertAlmostEqual(d,r)

        for d,r in zip(np.array(D['yerr']).flat,
                       np.array(R['yerr']).flat):
            self.assertAlmostEqual(d,r)

    def test7(self):
        R = {'aggregate': 'ci',
             'clevels': ['I', 'II'],
             'fname': 'output\\interaction_plot(SUPPRESSION~CYCLE_X_PHASE_X_GROUP,yerr=95% ci).png',
             'maintitle': 'SUPPRESSION by CYCLE * PHASE * GROUP',
             'numcols': 2,
             'numrows': 2,
             'rlevels': ['AA', 'AB'],
             'subplot_titles': ['GROUP = AA, PHASE = AA',
                                'GROUP = AA, PHASE = AA',
                                'GROUP = AB, PHASE = AB',
                                'GROUP = AB, PHASE = AB'],
             'xmaxs': [4.1500000000000004,
                       4.1500000000000004,
                       4.1500000000000004,
                       4.1500000000000004],
             'xmins': [0.84999999999999998,
                       0.84999999999999998,
                       0.84999999999999998,
                       0.84999999999999998],
             'y': [[ 13.2125,  16.3   ,  16.8125,  15.0875],
                   [ 14.5875,  19.1875,  15.1375,  17.675 ],
                   [  9.075 ,  16.1625,  14.5625,  11.6875],
                   [ 15.7125,  27.1125,  30.3   ,  32.3   ]],
             'yerr': [[  6.41377058,   4.90274323,   6.52638491,   4.723284  ],
                      [  7.98351964,   7.01554694,   5.50066923,   4.7712851 ],
                      [  4.06006718,   6.15225848,   4.21669129,   6.23708923],
                      [  4.55687267,   7.52964629,   8.43210133,  10.3156968 ]],
             'ymax': 64.8719707118471,
             'ymin': 0.0}
        
        # separate y plots and separate x plots
        df=DataFrame()
        df.TESTMODE = True
        df.read_tbl('data\suppression~subjectXgroupXageXcycleXphase.csv')

        D = df.interaction_plot('SUPPRESSION','CYCLE',
                                sepxplots='PHASE',
                                sepyplots='GROUP',
                                yerr='ci',
                                where=[('GROUP','not in',['LAB'])],
                                output_dir='output')
        
        self.assertEqual(D['aggregate'],      R['aggregate'])
        self.assertEqual(D['clevels'],        R['clevels'])
        self.assertEqual(D['rlevels'],        R['rlevels'])
        self.assertEqual(D['numcols'],        R['numcols'])
        self.assertEqual(D['numrows'],        R['numrows'])
        self.assertEqual(D['fname'],          R['fname'])
        self.assertEqual(D['maintitle'],      R['maintitle'])
        self.assertEqual(D['subplot_titles'], R['subplot_titles'])
        self.assertAlmostEqual(D['ymin'],     R['ymin'])
        self.assertAlmostEqual(D['ymax'],     R['ymax'])
        
        for d,r in zip(np.array(D['y']).flat,
                       np.array(R['y']).flat):
            self.assertAlmostEqual(d,r)

        for d,r in zip(np.array(D['yerr']).flat,
                       np.array(R['yerr']).flat):
            self.assertAlmostEqual(d,r)


def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_interaction_plot)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
