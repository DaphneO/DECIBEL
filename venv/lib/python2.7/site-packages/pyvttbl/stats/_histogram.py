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
from collections import Counter,OrderedDict
from copy import copy

# third party modules
import pystaggrelite3

# included modules
from pyvttbl.misc.texttable import Texttable as TextTable
from pyvttbl.misc.support import *

class Histogram(OrderedDict):
    def __init__(self, *args, **kwds):
        if len(args) > 1:
            raise Exception('expecting only 1 argument')

        if kwds.has_key('cname'):
            self.cname = kwds['cname']
        else:
            self.cname = None

        if kwds.has_key('bins'):
            self.bins = kwds['bins']
        else:
            self.bins = 10.

        if kwds.has_key('range'):
            self.range = kwds['range']
        else:
            self.range = None

        if kwds.has_key('density'):
            self.density = kwds['density']
        else:
            self.density = False

        if kwds.has_key('cumulative'):
            self.cumulative = kwds['cumulative']
        else:
            self.cumulative = False 
            
        if len(args) == 1:
            super(Histogram, self).__init__(args[0])
        else:
            super(Histogram, self).__init__()
            
    def run(self, V, cname=None, bins=10,
                 range=None, density=False, cumulative=False):   
        """
        generates and stores histogram data for numerical data in V
        """
        
        super(Histogram, self).__init__()

        
        try:
            V = sorted(_flatten(list(V)))
        except:
            raise TypeError('V must be a list-like object')

        if len(V) == 0:
            raise Exception('V has zero length')
            
        if cname == None:
            self.cname = ''
        else:
            self.cname = cname

        values, bin_edges = pystaggrelite3.hist(V, bins=bins,
                   range=range, density=density, cumulative=cumulative)

        self['values'] = values
        self['bin_edges'] = bin_edges
        
        if cname == None:
            self.cname = ''
        else:
            self.cname = cname
            
        self.bins = bins
        self.range = range
        self.density = density
        self.cumulative = cumulative
        
    def __str__(self):

        tt = TextTable(48)
        tt.set_cols_dtype(['f', 'f'])
        tt.set_cols_align(['r', 'r'])
        for (b, v) in zip(self['bin_edges'],self['values']+['']):
            tt.add_row([b, v])
        tt.set_deco(TextTable.HEADER)
        tt.header(['Bins','Values'])

        return ''.join([('','Cumulative ')[self.cumulative],
                        ('','Density ')[self.density],
                        'Histogram for ', self.cname, '\n',
                        tt.draw()])

    def __repr__(self):
        if self == {}:
            return 'Histogram()'
        
        s = []
        for k, v in self.items():
            s.append("('%s', %s)"%(k, repr(v)))
        args = '[' + ', '.join(s) + ']'
        
        kwds = []            
        if self.cname != None:
            kwds.append(", cname='%s'"%self.cname)

        if self.bins != 10:
            kwds.append(', bins=%s'%self.bins)

        if self.range != None:
            kwds.append(', range=%s'%repr(range))

        if self.density != False:
            kwds.append(', density=%s'%density)
            
        if self.cumulative != False:
            kwds.append(', cumulative=%s'%cumulative)
            
        kwds= ''.join(kwds)

        return 'Histogram(%s%s)'%(args, kwds)
