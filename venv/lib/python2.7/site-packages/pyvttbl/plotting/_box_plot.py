from __future__ import print_function

# Copyright (c) 2012, Roger Lew [see LICENSE.txt]

# Python 2 to 3 workarounds
import sys
if sys.version_info[0] == 2:
    _strobj = basestring
    _xrange = xrange
elif sys.version_info[0] == 3:
    _strobj = str
    _xrange = range
    
import os

import pylab
import numpy as np
from collections import Counter

from pyvttbl.misc.support import _flatten

def box_plot(df, val, factors=None, where=None,
        fname=None, output_dir='', quality='medium'):
    """
    Makes a box plot

    args:
       df:
          a pyvttbl.DataFrame object
          
       val:
          the label of the dependent variable

    kwds:
       factors:
          a list of factors to include in boxplot
          
       where:
          a string, list of strings, or list of tuples
          applied to the DataFrame before plotting
          
       fname:
          output file name
          
       quality:
          {'low' | 'medium' | 'high'} specifies image file dpi
    """

    if factors == None:
        factors = []

    if where == None:
        where = []

    # check to see if there is any data in the table
    if df == {}:
        raise Exception('Table must have data to print data')
    
    # check to see if data columns have equal lengths
    if not df._are_col_lengths_equal():
        raise Exception('columns have unequal lengths')

    # check the supplied arguments
    if val not in df.keys():
        raise KeyError(val)

    if not hasattr(factors, '__iter__'):
        raise TypeError( "'%s' object is not iterable"
                         % type(factors).__name__)
    
    for k in factors:
        if k not in df.keys():
            raise KeyError(k)
        
    # check for duplicate names
    dup = Counter([val]+factors)
    del dup[None]
    if not all([count==1 for count in dup.values()]):
        raise Exception('duplicate labels specified as plot parameters')

    # check fname
    if not isinstance(fname, _strobj) and fname != None:
        raise TypeError('fname must be None or string')

    if isinstance(fname, _strobj):
        if not (fname.lower().endswith('.png') or \
                fname.lower().endswith('.svg')):
            raise Exception('fname must end with .png or .svg')

    test = {}

    if factors == []:
        d = df.select_col(val, where=where)            
        fig = pylab.figure()
        pylab.boxplot(np.array(d))
        xticks = pylab.xticks()[0]
        xlabels = [val]
        pylab.xticks(xticks, xlabels)

        test['d'] = d
        test['val'] = val

    else:
        D = df.pivot(val, rows=factors,
                       where=where,
                       aggregate='tolist')

        fig = pylab.figure(figsize=(6*len(factors),6))
        fig.subplots_adjust(left=.05, right=.97, bottom=0.24)
        pylab.boxplot([np.array(_flatten(d)) for d in D])
        xticks = pylab.xticks()[0]
        xlabels = ['\n'.join('%s = %s'%fc for fc in c) for c in D.rnames]
        pylab.xticks(xticks, xlabels,
                     rotation=35,
                     verticalalignment='top')

        test['d'] = [np.array(_flatten(d)) for d in D]
        test['xlabels'] = xlabels

    maintitle = '%s'%val

    if factors != []:
        maintitle += ' by '
        maintitle += ' * '.join(factors)
        
    fig.text(0.5, 0.95, maintitle,
             horizontalalignment='center',
             verticalalignment='top')
    
    test['maintitle'] = maintitle
        
    if fname == None:
        fname = 'box(%s'%val
        if factors != []:
            fname += '~' + '_X_'.join([str(f) for f in factors])
        fname += ').png'

    fname = os.path.join(output_dir, fname)
    
    test['fname'] = fname
    
    # save figure
    if quality == 'low' or fname.endswith('.svg'):
        pylab.savefig(fname)
        
    elif quality == 'medium':
        pylab.savefig(fname, dpi=200)
        
    elif quality == 'high':
        pylab.savefig(fname, dpi=300)
        
    else:
        pylab.savefig(fname)

    pylab.close()

    if df.TESTMODE:
        return test
