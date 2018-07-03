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
##from pyvttbl.plotting import box_plot
from pyvttbl.misc.support import *

class Test_marginals(unittest.TestCase):
    def test0(self):
        df=DataFrame()
        df.read_tbl('data/words~ageXcondition.csv')

        x=df.marginals('WORDS',factors=['AGE','CONDITION'])

        for d,r in zip(x['dmu'],[11,7,13.4,12,6.9,14.8,6.5,17.6,19.3,7.6]):
            self.failUnlessAlmostEqual(d,r)

        for d,r in zip(x['dN'],[10,10,10,10,10,10,10,10,10,10]):
            self.failUnlessAlmostEqual(d,r)

        for d,r in zip(x['dsem'],[0.788810638,
                                  0.577350269,
                                  1.423610434,
                                  1.183215957,
                                  0.674124947,
                                  1.103529690,
                                  0.453382350,
                                  0.819213715,
                                  0.843932593,
                                  0.618241233]):
            self.failUnlessAlmostEqual(d,r)

    def test02(self):
        
        R = """\
 AGE    CONDITION    Mean    Count   Std.    95% CI   95% CI 
                                     Error   lower    upper  
============================================================
old     adjective   11.000   10      0.789    9.454   12.546 
old     counting     7.000   10      0.577    5.868    8.132 
old     imagery     13.400   10      1.424   10.610   16.190 
old     intention   12.000   10      1.183    9.681   14.319 
old     rhyming      6.900   10      0.674    5.579    8.221 
young   adjective   14.800   10      1.104   12.637   16.963 
young   counting     6.500   10      0.453    5.611    7.389 
young   imagery     17.600   10      0.819   15.994   19.206 
young   intention   19.300   10      0.844   17.646   20.954 
young   rhyming      7.600   10      0.618    6.388    8.812 """
        
        df=DataFrame()
        df.read_tbl('data/words~ageXcondition.csv')
        D = df.marginals('WORDS',factors=['AGE','CONDITION'])
        self.assertEqual(str(D), R)

    def test03(self):
        R = """Marginals([('factorials', OrderedDict([('AGE', [u'old', u'old', u'old', u'old', u'old', u'young', u'young', u'young', u'young', u'young']), ('CONDITION', [u'adjective', u'counting', u'imagery', u'intention', u'rhyming', u'adjective', u'counting', u'imagery', u'intention', u'rhyming'])])), ('dmu', [11.0, 7.0, 13.4, 12.0, 6.9000000000000004, 14.800000000000001, 6.5, 17.600000000000001, 19.300000000000001, 7.5999999999999996]), ('dN', [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]), ('dsem', [0.78881063774661542, 0.57735026918962573, 1.4236104336041748, 1.1832159566199232, 0.67412494720522276, 1.1035296904831231, 0.4533823502911814, 0.81921371516296715, 0.84393259341147731, 0.61824123303304679]), ('dlower', [9.4539311500166345, 5.868393472388334, 10.609723550135818, 9.6808967250249509, 5.578715103477764, 12.637081806653079, 5.6113705934292843, 15.994341118280586, 17.645892116913505, 6.3882471832552277]), ('dupper', [12.546068849983365, 8.131606527611666, 16.190276449864182, 14.319103274975049, 8.2212848965222367, 16.962918193346923, 7.3886294065707157, 19.205658881719415, 20.954107883086497, 8.8117528167447716])], val='WORDS', factors=['AGE', 'CONDITION'])"""

        df=DataFrame()
        df.read_tbl('data/words~ageXcondition.csv')
        D = repr(df.marginals('WORDS',factors=['AGE','CONDITION']))
                
##        self.assertEqual(D, R)

    def test04(self):
        R = """\
AGE   CONDITION    Mean    Count   Std.    95% CI   95% CI 
                                   Error   lower    upper  
==========================================================
old   adjective   11.000   10      0.789    9.454   12.546 
old   counting     7.000   10      0.577    5.868    8.132 
old   imagery     13.400   10      1.424   10.610   16.190 
old   intention   12.000   10      1.183    9.681   14.319 
old   rhyming      6.900   10      0.674    5.579    8.221 """
        
        df=DataFrame()
        df.read_tbl('data/words~ageXcondition.csv')
        D = str(df.marginals('WORDS',
                              factors=['AGE','CONDITION'],
                              where='AGE == "old"'))
        self.assertEqual(D, R)

    def test05(self):
        R = """Marginals([('factorials', OrderedDict([('AGE', [u'old', u'old', u'old', u'old', u'old']), ('CONDITION', [u'adjective', u'counting', u'imagery', u'intention', u'rhyming'])])), ('dmu', [11.0, 7.0, 13.4, 12.0, 6.9000000000000004]), ('dN', [10, 10, 10, 10, 10]), ('dsem', [0.78881063774661542, 0.57735026918962573, 1.4236104336041748, 1.1832159566199232, 0.67412494720522276]), ('dlower', [9.4539311500166345, 5.868393472388334, 10.609723550135818, 9.6808967250249509, 5.578715103477764]), ('dupper', [12.546068849983365, 8.131606527611666, 16.190276449864182, 14.319103274975049, 8.2212848965222367])], val='WORDS', factors=['AGE', 'CONDITION'], where='AGE == "old"')"""

        df=DataFrame()
        df.read_tbl('data/words~ageXcondition.csv')
        D = df.marginals('WORDS',
                              factors=['AGE','CONDITION'],
                              where='AGE == "old"')

##        self.assertEqual(repr(D), R)


def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_marginals)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
