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
from collections import OrderedDict
from copy import copy

# third party
import scipy

# included modules
from pyvttbl.misc.support import _flatten
from pyvttbl.stats import _stats
from pyvttbl.stats._noncentral import nctcdf
from pyvttbl.misc.texttable import Texttable as TextTable

class Ttest(OrderedDict):
    """Student's t-test"""
    def __init__(self, *args, **kwds):
        if len(args) > 1:
            raise Exception('expecting only 1 argument')

        if kwds.has_key('paired'):
            self.paired = kwds['paired']
        else:
            self.paired = False

        if kwds.has_key('equal_variance'):
            self.equal_variance = kwds['equal_variance']
        else:
            self.equal_variance = True

        if kwds.has_key('alpha'):
            self.alpha = kwds['alpha']
        else:
            self.alpha = 0.05

        if kwds.has_key('aname'):
            self.aname = kwds['aname']
        else:
            self.aname = None
                
        if kwds.has_key('bname'):
            self.bname = kwds['bname']
        else:
            self.bname = None

        if kwds.has_key('type'):
            self.type = kwds['type']
        else:
            self.type = None
            
        if len(args) == 1:
            super(Ttest, self).__init__(args[0])
        else:
            super(Ttest, self).__init__()
            
    def run(self, A, B=None, pop_mean=None, paired=False, equal_variance=True,
                 alpha=0.05, aname=None, bname=None):
        """
        Compares the data in A to the data in B. If A or B are
        multidimensional they are flattened before testing.

        When paired is True, the equal_variance parameter has
        no effect, an exception is raised if A and B are not
        of equal length.
          t = \frac{\overline{X}_D - \mu_0}{s_D/\sqrt{n}}
          where:
            \overline{X}_D is the difference of the averages
            s_D is the standard deviation of the differences

          \mathrm{d.f.} = n_1 - 1

        When paired is False and equal_variance is True.
          t = \frac{\bar {X}_1 - \bar{X}_2}{S_{X_1X_2} \cdot \sqrt{\frac{1}{n_1}+\frac{1}{n_2}}}
          where:
          {S_{X_1X_2} is the pooled standard deviation
          computed as:
            S_{X_1X_2} = \sqrt{\frac{(n_1-1)S_{X_1}^2+(n_2-1)S_{X_2}^2}{n_1+n_2-2}}

          \mathrm{d.f.} = n_1 + n_2 - 2
          
        When paired is False and equal_variance is False.
          t = {\overline{X}_1 - \overline{X}_2 \over s_{\overline{X}_1 - \overline{X}_2}}
          where:
            s_{\overline{X}_1 - \overline{X}_2} = \sqrt{{s_1^2 \over n_1} + {s_2^2  \over n_2}}
            where:
            s_1^2 and s_2^2 are the unbiased variance estimates

          \mathrm{d.f.} = \frac{(s_1^2/n_1 + s_2^2/n_2)^2}{(s_1^2/n_1)^2/(n_1-1) + (s_2^2/n_2)^2/(n_2-1)}
        """

        A = _flatten(list(copy(A)))
##        try:
##            A = _flatten(list(copy(A)))
##        except:
##            raise TypeError('A must be a list-like object')
            
        try:
            if B != None:
                B = _flatten(list(copy(B)))
        except:
            raise TypeError('B must be a list-like object')

        if aname == None:
            self.aname = 'A'
        else:
            self.aname = aname

        if bname == None:
            self.bname = 'B'
        else:
            self.bname = bname
            
        self.A = A
        self.B = B
        self.paired = paired
        self.equal_variance = equal_variance
        self.alpha = alpha

        if B == None:
            t, prob2, n, df, mu, v = _stats.lttest_1samp(A, pop_mean)

            self.type = 't-Test: One Sample for means'
            self['t'] = t
            self['p2tail'] = prob2
            self['p1tail'] = prob2 / 2.
            self['n'] = n
            self['df'] = df
            self['mu'] = mu
            self['pop_mean'] = pop_mean
            self['var'] = v
            self['tc2tail'] = scipy.stats.t.ppf((1.-alpha),df)
            self['tc1tail'] = scipy.stats.t.ppf((1.-alpha/2.),df)

            # post-hoc power analysis
            self['cohen_d'] = abs( (pop_mean - mu) / math.sqrt(v) )
            self['delta'] = math.sqrt(n) *self['cohen_d']
            self['power1tail'] = 1. - nctcdf(self['tc2tail'], df, self['delta'])
            self['power2tail'] = 1. - nctcdf(self['tc1tail'], df, self['delta'])
            
                
        elif paired == True:
            if len(A) - len(B) != 0:
                raise Exception('A and B must have equal lengths '
                                'for paired comparisons')
            
            t, prob2, n, df, mu1, mu2, v1, v2 = _stats.ttest_rel(A, B)
            r, rprob2 = _stats.pearsonr(A,B)
            
            self.type = 't-Test: Paired Two Sample for means'
            self['t'] = t
            self['p2tail'] = prob2
            self['p1tail'] = prob2 / 2.
            self['n1'] = n
            self['n2'] = n
            self['r'] = r
            self['df'] = df
            self['mu1'] = mu1
            self['mu2'] = mu2
            self['var1'] = v1
            self['var2'] = v2
            self['tc2tail'] = scipy.stats.t.ppf((1.-alpha),df)
            self['tc1tail'] = scipy.stats.t.ppf((1.-alpha/2.),df)

            # post-hoc power analysis
            # http://www.psycho.uni-duesseldorf.de/abteilungen/aap/gpower3/download-and-register/Dokumente/GPower3-BRM-Paper.pdf
            sd1,sd2 = math.sqrt(v1), math.sqrt(v2)
            self['cohen_d'] = abs(mu1 - mu2) / math.sqrt(v1 + v2 - 2*r*sd1*sd2)
            self['delta'] = math.sqrt(n) *self['cohen_d']
            self['power1tail'] = 1. - nctcdf(self['tc2tail'], df, self['delta'])
            self['power2tail'] = 1. - nctcdf(self['tc1tail'], df, self['delta'])
            
        elif equal_variance:
            t, prob2, n1, n2, df, mu1, mu2, v1, v2, svar = _stats.ttest_ind(A, B)

            self.type = 't-Test: Two-Sample Assuming Equal Variances'
            self['t'] = t
            self['p2tail'] = prob2
            self['p1tail'] = prob2 / 2.
            self['n1'] = n1
            self['n2'] = n2
            self['df'] = df
            self['mu1'] = mu1
            self['mu2'] = mu2
            self['var1'] = v1
            self['var2'] = v2
            self['vpooled'] = svar
            self['tc2tail'] = scipy.stats.t.ppf((1.-alpha),df)
            self['tc1tail'] = scipy.stats.t.ppf((1.-alpha/2.),df)


            # post-hoc power analysis
            # http://www.psycho.uni-duesseldorf.de/abteilungen/aap/gpower3/download-and-register/Dokumente/GPower3-BRM-Paper.pdf
            # 
            # the pooled standard deviation is calculated as:
            #     sqrt((v1+v2)/2.)
            # although wikipedia suggests a more sophisticated estimate might be preferred:
            #     sqrt(((n1-1)*v1 + (n2-1)*v2)/(n1+n2))
            #
            # the biased estimate is used so that the results agree with G*power
            
            s = math.sqrt((v1+v2)/2.)
            self['cohen_d'] = abs(mu1 - mu2) / s
            self['delta'] = math.sqrt((n1*n2)/(n1+n2)) *self['cohen_d']
            self['power1tail'] = 1. - nctcdf(self['tc2tail'], df, self['delta'])
            self['power2tail'] = 1. - nctcdf(self['tc1tail'], df, self['delta'])
            
        else:            
            t, prob2, n1, n2, df, mu1, mu2, v1, v2 = _stats.ttest_ind_uneq(A, B)
        
            self.type = 't-Test: Two-Sample Assuming Unequal Variances'
            self['t'] = t
            self['p2tail'] = prob2
            self['p1tail'] = prob2 / 2.
            self['n1'] = n1
            self['n2'] = n2
            self['df'] = df
            self['mu1'] = mu1
            self['mu2'] = mu2
            self['var1'] = v1
            self['var2'] = v2
            self['tc2tail'] = scipy.stats.t.ppf((1.-alpha),df)
            self['tc1tail'] = scipy.stats.t.ppf((1.-alpha/2.),df)          

            # post-hoc power analysis
            # http://www.psycho.uni-duesseldorf.de/abteilungen/aap/gpower3/download-and-register/Dokumente/GPower3-BRM-Paper.pdf
            # 
            # the pooled standard deviation is calculated as:
            #     sqrt((v1+v2)/2.)
            # although wikipedia suggests a more sophisticated estimate might be preferred:
            #     sqrt(((n1-1)*v1 + (n2-1)*v2)/(n1+n2))
            #
            # the biased estimate is used so that the results agree with G*power
            
            s = math.sqrt((v1+v2)/2.)
            self['cohen_d'] = abs(mu1 - mu2) / s
            self['delta'] = math.sqrt((n1*n2)/(n1+n2)) *self['cohen_d']
            self['power1tail'] = 1. - nctcdf(self['tc2tail'], df, self['delta'])
            self['power2tail'] = 1. - nctcdf(self['tc1tail'], df, self['delta'])
            
    def __str__(self):

        if self == {}:
            return '(no data in object)'


        if self.B == None:
            tt = TextTable(max_width=100000000)
            tt.set_cols_dtype(['t', 'a'])
            tt.set_cols_align(['l', 'r'])
            tt.set_deco(TextTable.HEADER)

            first = 't-Test: One Sample for means\n'
            tt.header( ['',                        self.aname])
            tt.add_row(['Sample Mean',             self['mu']])
            tt.add_row(['Hypothesized Pop. Mean',  self['pop_mean']])
            tt.add_row(['Variance',                self['var']])
            tt.add_row(['Observations',            self['n']])
            tt.add_row(['df',                      self['df']])
            tt.add_row(['t Stat',                  self['t']])
            tt.add_row(['alpha',                   self.alpha])
            tt.add_row(['P(T<=t) one-tail',        self['p1tail']])
            tt.add_row(['t Critical one-tail',     self['tc1tail']])
            tt.add_row(['P(T<=t) two-tail',        self['p2tail']])
            tt.add_row(['t Critical two-tail',     self['tc2tail']])
            tt.add_row(['P(T<=t) two-tail',        self['p2tail']])
            tt.add_row(['Effect size d',           self['cohen_d']])
            tt.add_row(['delta',                   self['delta']])
            tt.add_row(['Observed power one-tail', self['power1tail']])
            tt.add_row(['Observed power two-tail', self['power2tail']])

            return '%s\n%s'%(first, tt.draw())


        tt = TextTable(max_width=100000000)
        tt.set_cols_dtype(['t', 'a', 'a'])
        tt.set_cols_align(['l', 'r', 'r'])
        tt.set_deco(TextTable.HEADER)
        
        if self.paired == True:
            first = 't-Test: Paired Two Sample for means\n'
            tt.header( ['',                        self.aname,         self.bname])
            tt.add_row(['Mean',                    self['mu1'],        self['mu2']])
            tt.add_row(['Variance',                self['var1'],       self['var2']])
            tt.add_row(['Observations',            self['n1'],         self['n2']])
            tt.add_row(['Pearson Correlation',     self['r'],          ''])
            tt.add_row(['df',                      self['df'],         ''])
            tt.add_row(['t Stat',                  self['t'],          ''])
            tt.add_row(['alpha',                   self.alpha,         ''])
            tt.add_row(['P(T<=t) one-tail',        self['p1tail'],     ''])
            tt.add_row(['t Critical one-tail',     self['tc1tail'],    ''])
            tt.add_row(['P(T<=t) two-tail',        self['p2tail'],     ''])
            tt.add_row(['t Critical two-tail',     self['tc2tail'],    ''])
            tt.add_row(['P(T<=t) two-tail',        self['p2tail'],     ''])
            tt.add_row(['Effect size dz',          self['cohen_d'],    ''])
            tt.add_row(['delta',                   self['delta'],      ''])
            tt.add_row(['Observed power one-tail', self['power1tail'], ''])
            tt.add_row(['Observed power two-tail', self['power2tail'], ''])

        elif self.equal_variance:
            first = 't-Test: Two-Sample Assuming Equal Variances\n'
            tt.header( ['',                        self.aname,      self.bname])
            tt.add_row(['Mean',                    self['mu1'],     self['mu2']])
            tt.add_row(['Variance',                self['var1'],    self['var2']])
            tt.add_row(['Observations',            self['n1'],      self['n2']])
            tt.add_row(['Pooled Variance',         self['vpooled'], ''])
            tt.add_row(['df',                      self['df'],      ''])
            tt.add_row(['t Stat',                  self['t'],          ''])
            tt.add_row(['alpha',                   self.alpha,         ''])
            tt.add_row(['P(T<=t) one-tail',        self['p1tail'],     ''])
            tt.add_row(['t Critical one-tail',     self['tc1tail'],    ''])
            tt.add_row(['P(T<=t) two-tail',        self['p2tail'],     ''])
            tt.add_row(['t Critical two-tail',     self['tc2tail'],    ''])
            tt.add_row(['P(T<=t) two-tail',        self['p2tail'],     ''])
            tt.add_row(['Effect size d',           self['cohen_d'],    ''])
            tt.add_row(['delta',                   self['delta'],      ''])
            tt.add_row(['Observed power one-tail', self['power1tail'], ''])
            tt.add_row(['Observed power two-tail', self['power2tail'], ''])
        
        else:
            first = 't-Test: Two-Sample Assuming Unequal Variances\n'
            tt.header( ['',                        self.aname,      self.bname])
            tt.add_row(['Mean',                    self['mu1'],     self['mu2']])
            tt.add_row(['Variance',                self['var1'],    self['var2']])
            tt.add_row(['Observations',            self['n1'],      self['n2']])
            tt.add_row(['df',                      self['df'],      ''])
            tt.add_row(['t Stat',                  self['t'],          ''])
            tt.add_row(['alpha',                   self.alpha,         ''])
            tt.add_row(['P(T<=t) one-tail',        self['p1tail'],     ''])
            tt.add_row(['t Critical one-tail',     self['tc1tail'],    ''])
            tt.add_row(['P(T<=t) two-tail',        self['p2tail'],     ''])
            tt.add_row(['t Critical two-tail',     self['tc2tail'],    ''])
            tt.add_row(['P(T<=t) two-tail',        self['p2tail'],     ''])
            tt.add_row(['Effect size d',           self['cohen_d'],    ''])
            tt.add_row(['delta',                   self['delta'],      ''])
            tt.add_row(['Observed power one-tail', self['power1tail'], ''])
            tt.add_row(['Observed power two-tail', self['power2tail'], ''])
            
        return ''.join([first,tt.draw()])

    def __repr__(self):
        if self == {}:
            return 'Ttest()'

        s = []
        for k, v in self.items():
            s.append("('%s', %s)"%(k, repr(v)))
        args = '[' + ', '.join(s) + ']'
        
        kwds = []            
        if self.paired != False:
            kwds.append(", paired=%s"%self.paired)

        if self.equal_variance != True:
            kwds.append(", equal_variance=%s"%self.equal_variance)

        if self.alpha != 0.05:
            kwds.append(", alpha=%s"%self.alpha)

        if self.aname != None:
            kwds.append(", aname='%s'"%self.aname)
            
        if self.bname != None:
            kwds.append(", bname='%s'"%self.bname)
            
        if self.type != None:
            kwds.append(", type='%s'"%self.type)
                
        kwds= ''.join(kwds)
        
        return 'Ttest(%s%s)'%(args,kwds)
