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

from pyvttbl import DataFrame
from pyvttbl.misc.support import *

class Test_validate_for_success(unittest.TestCase):
    def test0(self):

        df=DataFrame()
        df.read_tbl('data\suppression~subjectXgroupXageXcycleXphase.csv')
        df['RANDDATA'][42]=0.

        R=df.validate({'GROUP' : lambda x: x in ['AA', 'AB', 'LAB'],
                         'SEX' : lambda x: x in [0],
                 'SUPPRESSION' : lambda x: x < 62.,
                    'RANDDATA' : lambda x: x!=0,
                     'SUBJECT' : _isint}, verbose=False, report=False)
        self.assertFalse(R)


    def test1(self):

        df=DataFrame()
        df.read_tbl('data\suppression~subjectXgroupXageXcycleXphase.csv')
        ##df['RANDDATA'][42]='nan'

        R=df.validate({'GROUP' : lambda x: x in ['AA', 'AB', 'LAB'],
                         'SEX' : lambda x: x in [0,1],
                 'SUPPRESSION' : lambda x: x < 1000.,
                    'RANDDATA' : lambda x: _isfloat(x),
                     'SUBJECT' : _isint}, verbose=False, report=False)
        self.assertTrue(R)
        
    def test2(self):

        df=DataFrame()
        df.read_tbl('data\suppression~subjectXgroupXageXcycleXphase.csv')
        ##df['RANDDATA'][42]='nan'

        R=df.validate({'GROUP' : lambda x: x in ['AA', 'AB', 'LAB'],
                         'SEX' : lambda x: x in [0,1],
                 'SUPPRESSION' : lambda x: x < 1000.,
                    'RANDDATA' : lambda x: _isfloat(x) and not isnan(x),
                     'SUBJECT' : _isint(1),
                  'NOT_A_COL1' : _isint,
                  'NOT_A_COL2' : _isint}, verbose=False, report=False)
        self.assertFalse(R)

class Test_validate_for_failure(unittest.TestCase):
    def test3(self):
        df=DataFrame()
        
        with self.assertRaises(Exception) as cm:
            df.validate({'GROUP' : lambda x: x in ['AA', 'AB', 'LAB']})

        self.assertEqual(str(cm.exception),
                         'table must have data to validate data')

    def test4(self):
        df=DataFrame()
        df.insert([('GROUP','AA'),('VAL',1)])
        
        with self.assertRaises(Exception) as cm:
            df.validate(lambda x: x in ['AA', 'AB', 'LAB'])

        self.assertEqual(str(cm.exception),
                         'criteria must be mappable type')
        
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_validate_for_success),
            unittest.makeSuite(Test_validate_for_failure),
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
    
