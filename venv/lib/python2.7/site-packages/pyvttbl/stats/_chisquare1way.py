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

# std lib
import math
from collections import Counter,OrderedDict
from copy import copy

# third party
import scipy

# included modules
from pyvttbl.stats import _stats
from pyvttbl.stats._noncentral import ncx2cdf
from pyvttbl.misc.texttable import Texttable as TextTable
from pyvttbl.misc.support import *

def _flatten(x):
    """_flatten(sequence) -> list

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).

    Examples:
    >>> [1, 2, [3,4], (5,6)]
    [1, 2, [3, 4], (5, 6)]
    >>> _flatten([[[1,2,3], (42,None)], [4,5], [6], 7, MyVector(8,9,10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]"""

    result = []
    for el in x:
        #if isinstance(el, (list, tuple)):
        if hasattr(el, "__iter__") and not isinstance(el, _strobj):
            result.extend(_flatten(el))
        else:
            result.append(el)
    return result

def _str(x, dtype='a', n=3):
    """
    makes string formatting more human readable
    """
    try    : f=float(x)
    except : return str(x)

    if math.isnan(f) : return 'nan'
    if math.isinf(f) : return 'inf'
    
    if   dtype == 'i' : return str(int(round(f)))
    elif dtype == 'f' : return '%.*f'%(n, f)
    elif dtype == 'e' : return '%.*e'%(n, f)
    elif dtype == 't' : return str(x)
    else:
        if f-round(f) == 0:
            if abs(f) > 1e8:
                return '%.*e'%(n, f)
            else:
                return str(int(round(f)))
        else:
            if abs(f) > 1e8 or abs(f) < 1e-8:
                return '%.*e'%(n, f)
            else:
                return '%.*f'%(n, f)

class ChiSquare1way(OrderedDict):
    """1-way Chi-Square Test"""
    def __init__(self, *args, **kwds):
        if len(args) > 1:
            raise Exception('expecting only 1 argument')

        if kwds.has_key('measure'):
            self.measure = kwds['measure']
        else:
            self.measure = 'Measure'
            
        if kwds.has_key('conditions_list'):
            self.conditions_list = kwds['conditions_list']
        else:
            self.conditions_list = []
            
        if kwds.has_key('alpha'):
            self.alpha = kwds['alpha']
        else:
            self.alpha = 0.05

        if len(args) == 1:
            super(ChiSquare1way, self).__init__(args[0])
        else:
            super(ChiSquare1way, self).__init__()

    def run(self, observed, expected=None, conditions_list=None,
            measure='Measure', alpha=0.05):
        """
        
        """
        chisq, prob, df, expected = _stats.lchisquare(observed, expected)
        try:
            lnchisq, lnprob, lndf, lnexpected = \
                     _stats.llnchisquare(observed, expected)
        except:
            lnchisq, lnprob, lndf, lnexpected = 'nan','nan','nan','nan'
            
        self.observed = observed
        self.expected = expected
        self.alpha = alpha
        
        if conditions_list == None:
            self.conditions_list = []
            abc = lambda i : 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'\
                             [i%26]*(int(math.floor(i/26))+1)
            for i in _xrange(len(observed)):
                self.conditions_list.append(abc(i))
        else:
            self.conditions_list = conditions_list

        self['chisq'] = chisq
        self['p'] = prob
        self['df'] = df
        self['lnchisq'] = lnchisq
        self['lnp'] = lnprob
        self['lndf'] = lndf
        self['N'] = sum(observed)
        self.observed = observed
        self.expected = expected

        p_observed = [v/float(self['N']) for v in observed]
        p_expected = [v/float(self['N']) for v in expected]

        p_chisq = sum([(po-pe)**2/pe for po,pe in zip(p_observed,p_expected)])
        self['w'] = math.sqrt(p_chisq)
        self['lambda'] = p_chisq*self['N']
        self['crit_chi2'] = scipy.stats.chi2.ppf((1.-alpha),df)
        self['power'] = 1. - ncx2cdf(self['crit_chi2'],df,self['lambda'])

    def __str__(self):

        if self == {}:
            return '(no data in object)'

        # SUMMARY
        tt_s = TextTable(max_width=0)
        tt_s.set_cols_dtype(['t'] + ['a']*len(self.observed))
        tt_s.set_cols_align(['l'] + ['r']*len(self.observed))
        tt_s.set_deco(TextTable.HEADER)

        tt_s.header( [' '] + self.conditions_list)

        tt_s.add_row(['Observed'] + self.observed)
        tt_s.add_row(['Expected'] + self.expected)

        # TESTS
        tt_a = TextTable(max_width=0)
        tt_a.set_cols_dtype(['t', 'a', 'a', 'a'])
        tt_a.set_cols_align(['l', 'r', 'r', 'r'])
        tt_a.set_deco(TextTable.HEADER)

        tt_a.header([' ', 'Value', 'df', 'P'])
        tt_a.add_row(['Pearson Chi-Square',
                      self['chisq'], self['df'], self['p']])
        tt_a.add_row(['Likelihood Ratio',
                      self['lnchisq'], self['lndf'], self['lnp']])
        tt_a.add_row(['Observations', self['N'],'',''])

        # POWER
        tt_p = TextTable(max_width=0)
        tt_p.set_cols_dtype(['t', 'a'])
        tt_p.set_cols_align(['l', 'r'])
        tt_p.set_deco(TextTable.HEADER)

        tt_p.header( ['Measure',' '])

        tt_p.add_row(['Effect size w', self['w']])
        tt_p.add_row(['Non-centrality lambda', self['lambda']])
        tt_p.add_row(['Critical Chi-Square', self['crit_chi2']])
        tt_p.add_row(['Power', self['power']])
                     
        return 'Chi-Square: Single Factor\n\n' + \
               'SUMMARY\n%s\n\n'%tt_s.draw() + \
               'CHI-SQUARE TESTS\n%s\n\n'%tt_a.draw() + \
               'POST-HOC POWER\n%s'%tt_p.draw()
               

    def __repr__(self):
        if self == {}:
            return 'ChiSquare1way()'

        s = []
        for k, v in self.items():
            s.append("('%s', %s)"%(k, repr(v)))
        args = '[' + ', '.join(s) + ']'

        kwds = []
        if self.measure != 'Measure':
            kwds.append(', val="%s"'%self.measure)
            
        if self.conditions_list != []:
            kwds.append(', conditions_list=%s'%repr(self.conditions_list))
            
        if self.alpha != 0.05:
            kwds.append(', alpha=%s'%str(self.alpha))
            
        kwds= ''.join(kwds)
        
        return 'ChiSquare1way(%s%s)'%(args,kwds)

