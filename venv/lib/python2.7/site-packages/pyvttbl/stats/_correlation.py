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
import numpy as np

# included modules
from pyvttbl.stats import _stats
from pyvttbl.misc.texttable import Texttable as TextTable
from pyvttbl.misc.support import *

class Correlation(OrderedDict):
    """bivariate correlation matrix"""
    def __init__(self, *args, **kwds):
        if len(args) > 1:
            raise Exception('expecting only 1 argument')

        if kwds.has_key('conditions_list'):
            self.conditions_list = kwds['conditions_list']
        else:
            self.conditions_list = []
            
        if kwds.has_key('coefficient'):
            self.coefficient = kwds['coefficient']
        else:
            self.coefficient = 'pearson'
            
        if kwds.has_key('alpha'):
            self.alpha = kwds['alpha']
        else:
            self.alpha = 0.05
            
        if kwds.has_key('N'):
            self.N = kwds['N']
        else:
            self.N = 0

        if len(args) == 1:
            super(Correlation, self).__init__(args[0])
        else:
            super(Correlation, self).__init__()

    def run(self, list_of_lists, conditions_list=None,
            coefficient='pearson', alpha=0.05):
        """
        
        """

        # check list_of_lists
        if len(list_of_lists) < 2:
            raise Exception('expecting 2 or more items in variables list')

        lengths = [len(L) for L in list_of_lists]

        if not all(L-lengths[0]+1 for L in lengths):
            raise Exception('lists must be of equal length')

        # check coefficient
        if coefficient == 'pearson':
            func = _stats.pearsonr
        elif coefficient == 'spearman':
            func = _stats.spearmanr
        elif coefficient == 'pointbiserial':
            func = _stats.pointbiserialr
        elif coefficient == 'kendalltau':
            func = _stats.kendalltau
        else:
            raise Exception('invalid coefficient parameter')
        
        self.coefficient = coefficient
        
        # build or check conditions list
        if conditions_list == None:
            self.conditions_list = []
            abc = lambda i : 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'\
                             [i%26]*(int(math.floor(i/26))+1)
            for i in _xrange(len(list_of_lists)):
                self.conditions_list.append(abc(i))
        else:
            self.conditions_list = conditions_list

        if len(list_of_lists) != len(self.conditions_list):
            raise Exception('list_of_lists and conditions_list '
                            'must be of equal length')

        # put data into a dict
        d=dict([(k,v) for k,v in zip(self.conditions_list, list_of_lists)])

        # run correlations
        for x,y in _xunique_combinations(self.conditions_list, 2):
            r, prob = func(d[x],d[y])
            self[(x,y)] = dict(r=r, p=prob)

        self.alpha = alpha
        self.N = lengths[0]

        self.lm_significance_testing()
        
    def lm_significance_testing(self):
        """
        Performs Larzelere and Mulaik Significance Testing
        on the paired correlations in self.

        The testing follows a stepdown procedure similiar
        to the Holm for multiple comparisons.
        The absolute r values are are arranged in decreasing
        order and the significant alpha level is adjusted
        according to alpha/(k-i+1) where k is the total
        number of tests and i the current pair.
        """
        
        # perform post_hoc analysis
        L = [(key, abs(self[key]['r'])) for key in self]
        k = len(self)
        self.lm = []
        for i,(pair,r) in enumerate(sorted(
                              L, key=lambda t: t[1], reverse=True)):
            adj_alpha = self.alpha / (k - (i + 1) + 1)
            self.lm.append([pair, i+1, r, self[pair]['p'], adj_alpha])
        
    def __str__(self):

        if self == {}:
            return '(no data in object)'

        tt = TextTable(max_width=0)
        tt.set_cols_dtype(['t', 't'] + ['a']*len(self.conditions_list))
        tt.set_cols_align(['l', 'l'] + ['r']*len(self.conditions_list))
        tt.set_deco(TextTable.HEADER | TextTable.HLINES)
        tt.header(['',''] + sorted(self.conditions_list))
        
        for a in sorted(self.conditions_list):
            rline = [a, self.coefficient]
            pline = ['', 'Sig (2-tailed)']
            nline = ['', 'N']
            for b in sorted(self.conditions_list):
                if a == b:
                    rline.append('1')
                    pline.append(' .')
                    nline.append(self.N)
                elif self.has_key((a,b)):
                    rline.append(self[(a,b)]['r'])
                    pline.append(self[(a,b)]['p'])
                    nline.append(self.N)
                elif self.has_key((b,a)):
                    rline.append(self[(b,a)]['r'])
                    pline.append(self[(b,a)]['p'])
                    nline.append(self.N)

            tt.add_row(['%s\n%s\n%s'%(_str(r),_str(p),_str(n))
                        for r,p,n in zip(rline,pline,nline)])

        tt_lm = TextTable(max_width=0)
        tt_lm.set_cols_dtype(['t', 'i', 'f', 'a', 'a', 't'])
        tt_lm.set_cols_align(['l', 'r', 'r', 'r', 'r', 'l'])
        tt_lm.set_deco(TextTable.HEADER)
        tt_lm.header(['Pair', 'i', 'Correlation', 'P', 'alpha/(k-i+1)', 'Sig.'])
        
        for row in self.lm:
            x, y = row[0]
            tt_lm.add_row(['%s vs. %s'%(x, y)] +
                          row[1:] +
                          ([''],['**'])[row[3] < row[4]])
            
        return 'Bivariate Correlations\n\n' + tt.draw() + \
               '\n\nLarzelere and Mulaik Significance Testing\n\n' + tt_lm.draw()

    def __repr__(self):
        if self == {}:
            return 'Correlation()'

        s = []
        for k, v in self.items():
            s.append("(%s, %s)"%(repr(k), repr(v)))
        args = '[' + ', '.join(s) + ']'

        kwds = []
            
        if self.conditions_list != []:
            kwds.append(', conditions_list=%s'%repr(self.conditions_list))
            
        if self.coefficient != 'pearson':
            kwds.append(", coefficient='%s'"%str(self.coefficient))

        if self.alpha != 0.05:
            kwds.append(', alpha=%s'%str(self.alpha))
            
        if self.N != 0:
            kwds.append(', N=%i'%self.N)
            
        kwds= ''.join(kwds)
        
        return 'Correlation(%s%s)'%(args,kwds)
    
