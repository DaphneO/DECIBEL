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
from pyvttbl.stats._noncentral import ncfcdf
from pyvttbl.stats.qsturng import qsturng, psturng
from pyvttbl.misc.texttable import Texttable as TextTable
from pyvttbl.misc.support import *
	    
class Anova1way(OrderedDict):
    def __init__(self, *args, **kwds):
        if len(args) > 1:
            raise Exception('expecting only 1 argument')

        if kwds.has_key('posthoc'):
            self.posthoc = kwds['posthoc']
        else:
            self.posthoc = 'tukey'

        if kwds.has_key('multtest'):
            self.multtest = kwds['multtest']
        else:
            self.multtest = None
            
        if kwds.has_key('val'):
            self.val = kwds['val']
        else:
            self.val = 'Measure'
            
        if kwds.has_key('factor'):
            self.factor = kwds['factor']
        else:
            self.factor = 'Factor'
            
        if kwds.has_key('conditions_list'):
            self.conditions_list = kwds['conditions_list']
        else:
            self.conditions_list = []
            
        if kwds.has_key('alpha'):
            self.alpha = kwds['alpha']
        else:
            self.alpha = 0.05

        if len(args) == 1:
            super(Anova1way, self).__init__(args[0])
        else:
            super(Anova1way, self).__init__()

    def run(self, list_of_lists, val='Measure',
            factor='Factor', conditions_list=None,
            posthoc='tukey', alpha=0.05):
        """
        performs a one way analysis of variance on the data in
        list_of_lists. Each sub-list is treated as a group. factor
        is a label for the independent variable and conditions_list
        is a list of labels for the different treatment groups.
        """
        self.L = list_of_lists
        self.val = val
        self.factor = factor
        self.alpha = alpha
        self.posthoc = posthoc
        
        if conditions_list == None:
            abc = lambda i : 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'\
                             [i%26]*(int(math.floor(i/26))+1)
            for i in _xrange(len(list_of_lists)):
                self.conditions_list.append(abc(i))
        else:
            self.conditions_list = conditions_list

        f, prob, ns, means, vars, ssbn, sswn, dfbn, dfwn = \
           _stats.lF_oneway(list_of_lists)

        mu = np.mean(_flatten(self.L))
        var = np.var(_flatten(self.L))
        
        self['f'] = f
        self['p'] = prob
        self['ns'] = ns
        self['mus'] = means
        self['vars'] = vars
        self['ssbn'] = ssbn
        self['sswn'] = sswn
        self['dfbn'] = dfbn
        self['dfwn'] = dfwn
        self['msbn'] = ssbn/dfbn
        self['mswn'] = sswn/dfwn
        self['eta2'] = ssbn/(sswn+ssbn)         
        self['lambda'] = sum([n*(y-mu)**2./var for n,y in zip(ns,means)])
        self['power'] = 1.-ncfcdf(scipy.stats.f(dfbn,dfwn).ppf(1.-alpha),
                                  dfbn,dfwn,self['lambda'])

        o_list_of_lists = _stats.obrientransform(list_of_lists)        
        o_f, o_prob, o_ns, o_means, o_vars, o_ssbn, o_sswn, o_dfbn, o_dfwn = \
           _stats.lF_oneway(o_list_of_lists)

        mu = np.mean(_flatten(o_list_of_lists))
        var = np.var(_flatten(o_list_of_lists))
        
        self['o_f'] = o_f
        self['o_p'] = o_prob
        self['o_ns'] = o_ns
        self['o_mus'] = o_means
        self['o_vars'] = o_vars
        self['o_ssbn'] = o_ssbn
        self['o_sswn'] = o_sswn
        self['o_dfbn'] = o_dfbn
        self['o_dfwn'] = o_dfwn
        self['o_msbn'] = o_ssbn/o_dfbn
        self['o_mswn'] = o_sswn/o_dfwn
        self['o_eta2'] = o_ssbn/(o_sswn+o_ssbn)         
        self['o_lambda'] = sum([n*(y-mu)**2./var for n,y in zip(o_ns,o_means)])
        self['o_power'] = 1.-ncfcdf(scipy.stats.f(o_dfbn,o_dfwn).ppf(1.-alpha),
                                    o_dfbn,o_dfwn,self['o_lambda'])

        if posthoc.lower() == 'tukey':
            self._tukey()

        elif posthoc.lower() == 'snk':
            self._snk()

    def _tukey(self):
        # http://www.utdallas.edu/~herve/abdi-NewmanKeuls2010-pretty.pdf
        # put means into a dict
        d = dict([(k,v) for k,v in zip(self.conditions_list, self['mus'])])

##        # calculate the number of comparisons
##        s = sum(range(len(d)))

        # calculate the number of observations per group
        s = min(self['ns'])
        
        # calculate critical studentized range q statistic
        k = len(d)
        df = sum(self['ns']) - k
        q_crit10 = qsturng(.9, k, df)
        q_crit05 = qsturng(.95, k, df)
        q_crit01 = qsturng(.99, k, df)

        # run correlations
        multtest = {}
        
        for x in sorted(self.conditions_list):
            for y in sorted(self.conditions_list):
                if not multtest.has_key((y,x)):
                    abs_diff = abs(d[x]-d[y])
                    q = abs_diff / math.sqrt(self['mswn']*(1./s))
                    sig = 'ns'
                    if  q > q_crit10:
                        sig = '+'
                    if q > q_crit05:
                        sig = '*'
                    if q > q_crit01:
                        sig += '*'
                    multtest[(x,y)] = dict(q=q,
                                           sig=sig,
                                           abs_diff=abs(d[x]-d[y]),
                                           q_crit10=q_crit10,
                                           q_crit05=q_crit05,
                                           q_crit01=q_crit01,
                                           q_k=k,
                                           q_df=df)

        self.multtest = multtest

    def _snk(self):
        # http://www.utdallas.edu/~herve/abdi-NewmanKeuls2010-pretty.pdf
        # put means into a dict
        d = dict([(k,v) for k,v in zip(self.conditions_list, self['mus'])])

        # calculate the number of observations per group
        s = min(self['ns'])

        # figure out differences between pairs
        L = {}
        for x in sorted(self.conditions_list):
            for y in sorted(self.conditions_list):
                if not L.has_key((y,x)) and x!=y:
                    L[(x,y)] = abs(d[x]-d[y])

        L = sorted(list(L.items()), key=lambda t: t[1], reverse=True)

        # calculate critical studentized range q statistic
        k = len(d)
        df = sum(self['ns']) - k
        
        multtest = []
        for i,(pair,abs_diff) in enumerate(L):
##            print (i,pair,abs_diff,k)
            
            if k>1:
                q = abs_diff / math.sqrt(self['mswn']*(1./s))
                p = psturng(q, k, df)
                sig = 'ns'
                if  p < .1  :  sig = '+'
                if p < .05  :  sig = '*'
                if p < .01  :  sig = '**'
                if p < .001 :  sig = '***'
                multtest.append([pair, i+1, abs_diff, q, k, df, p, sig])
            else:
                multtest.append([pair, i+1, abs_diff, np.NAN, np.NAN, np.NAN, np.NAN, sig])

            try:
                if L[i][1] != L[i+1][1]:
                    k -= 1
            except:
                pass

            last_diff = abs_diff


        self.multtest = multtest
        
    def __str__(self):

        if self == {}:
            return '(no data in object)'

        tt_s = TextTable(max_width=0)
        tt_s.set_cols_dtype(['t', 'a', 'a', 'a', 'a'])
        tt_s.set_cols_align(['l', 'r', 'r', 'r', 'r'])
        tt_s.set_deco(TextTable.HEADER)

        tt_s.header( ['Groups','Count','Sum', 'Average','Variance'])
        for g, c, a, v in zip(self.conditions_list,
                              self['ns'],
                              self['mus'],
                              self['vars']):
            tt_s.add_row([g, c, c * a, a, v])

        tt_o = TextTable(max_width=0)
        tt_o.set_cols_dtype(['t', 'a', 'a', 'a', 'a', 'a', 'a', 'a'])
        tt_o.set_cols_align(['l', 'r', 'r', 'r', 'r', 'r', 'r', 'r'])
        tt_o.set_deco(TextTable.HEADER | TextTable.FOOTER)

        tt_o.header( ['Source of Variation','SS','df','MS','F','P-value','eta^2','Obs. power'])
        tt_o.add_row(['Treatments',self['o_ssbn'],self['o_dfbn'],
                                   self['o_msbn'],self['o_f'],self['o_p'],
                                   self['o_eta2'],self['o_power']])
        tt_o.add_row(['Error', self['o_sswn'],self['o_dfwn'],
                               self['o_mswn'],' ', ' ',' ', ' '])
        tt_o.footer( ['Total',self['o_ssbn']+self['o_sswn'],
                              self['o_dfbn']+self['o_dfwn'],' ',' ',' ',' ', ' '])
        
        tt_a = TextTable(max_width=0)
        tt_a.set_cols_dtype(['t', 'a', 'a', 'a', 'a', 'a', 'a', 'a'])
        tt_a.set_cols_align(['l', 'r', 'r', 'r', 'r', 'r', 'r', 'r'])
        tt_a.set_deco(TextTable.HEADER | TextTable.FOOTER)

        tt_a.header( ['Source of Variation','SS','df','MS','F','P-value','eta^2','Obs. power'])
        tt_a.add_row(['Treatments',self['ssbn'],self['dfbn'],
                                   self['msbn'],self['f'],self['p'],
                                   self['eta2'],self['power']])
        tt_a.add_row(['Error', self['sswn'],self['dfwn'],
                               self['mswn'],' ', ' ',' ', ' '])
        tt_a.footer( ['Total',self['ssbn']+self['sswn'],
                              self['dfbn']+self['dfwn'],' ',' ',' ',' ', ' '])

        posthoc = ''
        if self.posthoc.lower() == 'tukey' and self.multtest != None:
            tt_m = TextTable(max_width=0)
            tt_m.set_cols_dtype(['t'] + ['a']*len(self.conditions_list))
            tt_m.set_cols_align(['l'] + ['l']*len(self.conditions_list))
            tt_m.set_deco(TextTable.HEADER | TextTable.FOOTER)
            tt_m.header([''] + sorted(self.conditions_list))
            
            for a in sorted(self.conditions_list):
                rline = [a]
                for b in sorted(self.conditions_list):
                    if a == b:
                        rline.append('0')
                    elif self.multtest.has_key((a,b)):
                        q = self.multtest[(a,b)]['q']
                        sig = self.multtest[(a,b)]['sig']
                        rline.append('%s %s'%(_str(q), sig))
                    else:
                        rline.append(' ')

                tt_m.add_row(rline)
            tt_m.footer(['']*(len(self.conditions_list) + 1))
            q_crit10 = self.multtest[(a,b)]['q_crit10']
            q_crit05 = self.multtest[(a,b)]['q_crit05']
            q_crit01 = self.multtest[(a,b)]['q_crit01']
            k = self.multtest[(a,b)]['q_k']
            df = self.multtest[(a,b)]['q_df']
            
            posthoc = 'POSTHOC MULTIPLE COMPARISONS\n\n'
            posthoc += 'Tukey HSD: Table of q-statistics\n'
            posthoc += tt_m.draw()
            posthoc += '\n  + p < .10 (q-critical[%i, %i] = %s)'%(k, df, q_crit10)
            posthoc += '\n  * p < .05 (q-critical[%i, %i] = %s)'%(k, df, q_crit05)
            posthoc += '\n ** p < .01 (q-critical[%i, %i] = %s)'%(k, df, q_crit01)

        if self.posthoc.lower() == 'snk' and self.multtest != None:

            tt_m = TextTable(max_width=0)
            tt_m.set_cols_dtype(['t', 'i', 'f', 'a', 'a', 'a', 'a', 't'])
            tt_m.set_cols_align(['l', 'r', 'r', 'r', 'r', 'r', 'r', 'l'])
            tt_m.set_deco(TextTable.HEADER)
            tt_m.header(['Pair', 'i', '|diff|', 'q', 'range', 'df', 'p', 'Sig.'])
            
            for row in self.multtest:
                x, y = row[0]
                    
                tt_m.add_row(['%s vs. %s'%(x, y)] +
                             [(v,'-')[np.isnan(v)] for v in row[1:-1]] +
                             [row[-1]])
            
            posthoc = 'POSTHOC MULTIPLE COMPARISONS\n\n'
            posthoc += 'SNK: Step-down table of q-statistics\n'
            posthoc += tt_m.draw()
            posthoc += '\n  + p < .10,   * p < .05,   ** p < .01,   *** p < .001'
            
        return 'Anova: Single Factor on %s\n\n'%self.val + \
               'SUMMARY\n%s\n\n'%tt_s.draw() + \
               "O'BRIEN TEST FOR HOMOGENEITY OF VARIANCE\n%s\n\n"%tt_o.draw() + \
               'ANOVA\n%s\n\n'%tt_a.draw() + \
               posthoc

    def __repr__(self):
        if self == {}:
            return 'Anova1way()'

        s = []
        for k, v in self.items():
            s.append("('%s', %s)"%(k, repr(v)))
        args = '[' + ', '.join(s) + ']'

        kwds = []
        if self.val != 'Measure':
            kwds.append(', val="%s"'%self.val)

        if self.posthoc != 'tukey':
            kwds.append(', posthoc="%s"'%self.posthoc)

        if self.multtest != None:
            kwds.append(', multtest=%s'%repr(self.multtest))
            
        if self.factor != 'Factor':
            kwds.append(', factor="%s"'%self.factor)
            
        if self.conditions_list != []:
            kwds.append(', conditions_list=%s'%repr(self.conditions_list))
            
        if self.alpha != 0.05:
            kwds.append(', alpha=%s'%str(self.alpha))
            
        kwds= ''.join(kwds)
        
        return 'Anova1way(%s%s)'%(args,kwds)
