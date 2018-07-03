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

class ChiSquare2way(OrderedDict):
    def __init__(self, *args, **kwds):
        if len(args) > 1:
            raise Exception('expecting only 1 argument')

        if kwds.has_key('counter'):
            self.counter = kwds['counter']
        else:
            self.counter = None

        if kwds.has_key('row_counter'):
            self.row_counter = kwds['row_counter']
        else:
            self.row_counter = None

        if kwds.has_key('col_counter'):
            self.col_counter = kwds['col_counter']
        else:
            self.col_counter = None

        if kwds.has_key('N_r'):
            self.N_r = kwds['N_r']
        else:
            self.N_r = None

        if kwds.has_key('N_c'):
            self.N_c = kwds['N_c']
        else:
            self.N_c = None

        if kwds.has_key('alpha'):
            self.alpha = kwds['alpha']
        else:
            self.alpha = 0.05
            
        if len(args) == 1:
            super(ChiSquare2way, self).__init__(args[0])
        else:
            super(ChiSquare2way, self).__init__()
            
    def run(self, row_factor, col_factor, alpha=0.05):   
        """
        runs a 2-way chi square on the matched data in row_factor
        and col_factor.
        """

        if len(row_factor) != len(col_factor):
            raise Exception('row_factor and col_factor must be equal lengths')

        counter = Counter()
        row_counter= Counter()
        col_counter= Counter()
        for r,c in zip(row_factor, col_factor):
            counter[(r,c)] += 1.
            row_counter[r] += 1.
            col_counter[c] += 1.

        N = float(sum(counter.values()))
        observed = []
        expected = []
        for r in sorted(row_counter):
            observed.append([])
            expected.append([])
            for c in sorted(col_counter):
                observed[-1].append(counter[(r,c)])
                expected[-1].append((row_counter[r]*col_counter[c])/N)

        N_r, N_c = len(row_counter), len(col_counter)
        df = (N_r - 1) * (N_c - 1)

        chisq = sum((o-e)**2/e for o,e in
                    zip(_flatten(observed),_flatten(expected)))
        prob = _stats.chisqprob(chisq, df)

        try:        
            lnchisq = 2.*sum(o*math.log(o/e) for o,e in
                             zip(_flatten(observed),_flatten(expected)))
            lnprob = _stats.chisqprob(lnchisq, df)
        except:
            lnchisq = 'nan'
            lnprob = 'nan'

        if N_r == N_c == 2:
            ccchisq = sum((abs(o-e)-0.5)**2/e for o,e in
                          zip(_flatten(observed),_flatten(expected)))
            ccprob = _stats.chisqprob(ccchisq, df)
        else:
            ccchisq = None
            ccprob = None
            

        def rprob(r,df):
            TINY = 1e-30
            t = r*math.sqrt(df/((1.0-r+TINY)*(1.0+r+TINY)))
            return _stats.betai(0.5*df,0.5,df/(df+t*t))
            
        k = min([N_r, N_c])
        cramerV = math.sqrt(chisq/(N*(k-1)))
        cramerV_prob = rprob(cramerV, N-2)
        C = math.sqrt(chisq/(chisq + N))
        C_prob = rprob(C, N-2)
                
        self['chisq'] = chisq
        self['p'] = prob
        self['df'] = df
        self['lnchisq'] = lnchisq
        self['lnp'] = lnprob
        self['ccchisq'] = ccchisq
        self['ccp'] = ccprob
        self['N'] = N
        self['C'] = C
        self['CramerV'] = cramerV
        self['CramerV_prob'] = cramerV_prob
        self['C'] = C
        self['C_prob'] = C_prob
        
        self.counter = counter
        self.row_counter = row_counter
        self.col_counter = col_counter
        self.N_r = N_r
        self.N_c = N_c

        p_observed = [v/float(self['N']) for v in _flatten(observed)]
        p_expected = [v/float(self['N']) for v in _flatten(expected)]

        p_chisq = sum([(po-pe)**2/pe for po,pe in zip(p_observed,p_expected)])
        self['w'] = math.sqrt(p_chisq)
        self['lambda'] = p_chisq*self['N']
        self['crit_chi2'] = scipy.stats.chi2.ppf((1.-alpha),df)
        self['power'] = 1. - ncx2cdf(self['crit_chi2'],df,self['lambda'])
        
    def __str__(self):
        """Returns human readable string representation of ChiSquare2way"""

        if self == {}:
            return '(no data in object)'

        # SUMMARY
        tt_s = TextTable(max_width=0)
        tt_s.set_cols_dtype(['t'] + ['a']*(self.N_c + 1))
        tt_s.set_cols_align(['l'] + ['r']*(self.N_c + 1))
        tt_s.set_deco(TextTable.HEADER | TextTable.FOOTER)
        tt_s.header( [' '] + sorted(self.col_counter) + ['Total'])

        for r, rv in sorted(self.row_counter.items()):
            line = [r]
            for c, cv in sorted(self.col_counter.items()):
                o = self.counter[(r,c)]
                e = (rv*cv)/self['N']
                line.append('%s\n(%s)'%(_str(o), _str(e)))
            line.append(rv)
            tt_s.add_row(line)
        tt_s.footer(['Total'] +
                    [v for c,v in sorted(self.col_counter.items())] +
                    [self['N']])
    
        # SYMMETRIC TESTS
        tt_sym = TextTable(max_width=0)
        tt_sym.set_cols_dtype(['t', 'a', 'a'])
        tt_sym.set_cols_align(['l', 'r', 'r'])
        tt_sym.set_deco(TextTable.HEADER)
        tt_sym.header(['','Value','Approx.\nSig.'])
        tt_sym.add_row(["Cramer's V", self['CramerV'], self['CramerV_prob']])
        tt_sym.add_row(["Contingency Coefficient", self['C'], self['C_prob']])
        tt_sym.add_row(["N of Valid Cases", self['N'], ''])
                              
        # CHI-SQUARE TESTS
        tt_a = TextTable(max_width=0)
        tt_a.set_cols_dtype(['t', 'a', 'a', 'a'])
        tt_a.set_cols_align(['l', 'r', 'r', 'r'])
        tt_a.set_deco(TextTable.HEADER)
        tt_a.header([' ', 'Value', 'df', 'P'])
        tt_a.add_row(['Pearson Chi-Square',
                      self['chisq'], self['df'], self['p']])
        if self['ccchisq'] != None:
            tt_a.add_row(['Continuity Correction',
                          self['ccchisq'], self['df'], self['ccp']])
        tt_a.add_row(['Likelihood Ratio',
                      self['lnchisq'], self['df'], self['lnp']])
        tt_a.add_row(["N of Valid Cases", self['N'], '', ''])

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
        
        return 'Chi-Square: two Factor\n\n' + \
               'SUMMARY\n%s\n\n'%tt_s.draw() + \
               'SYMMETRIC MEASURES\n%s\n\n'%tt_sym.draw() + \
               'CHI-SQUARE TESTS\n%s\n\n'%tt_a.draw() + \
               'CHI-SQUARE POST-HOC POWER\n%s'%tt_p.draw()

    def __repr__(self):
        if self == {}:
            return 'ChiSquare2way()'
        
        s = []
        for k, v in self.items():
            s.append("('%s', %s)"%(k, repr(v)))
        args = '[' + ', '.join(s) + ']'
        
        kwds = []                        
        if self.counter != None:
            kwds.append(', counter=%s'%repr(self.counter))

        if self.row_counter != None:
            kwds.append(', row_counter=%s'%repr(self.row_counter))

        if self.col_counter != None:
            kwds.append(', col_counter=%s'%repr(self.col_counter))

        if self.N_r != None:
            kwds.append(', N_r=%i'%self.N_r)

        if self.N_c != None:
            kwds.append(', N_c=%i'%self.N_c)

        if self.alpha != 0.05:
            kwds.append(', alpha=%s'%str(self.alpha))
            
        return 'ChiSquare2way(%s%s)'%(args, ''.join(kwds))
    
