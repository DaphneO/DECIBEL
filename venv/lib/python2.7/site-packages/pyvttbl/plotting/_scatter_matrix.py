from __future__ import print_function

# Copyright (c) 2011, Roger Lew [see LICENSE.txt]

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
import scipy
import numpy as np

from pyvttbl.misc.support import *
from pyvttbl.plotting.support import \
     _bivariate_trend_fit, _tick_formatter, _subplots

def scatter_matrix(df, variables, alpha=0.5, grid=False,
                   diagonal=None, trend='linear', alternate_labels=True,
                   fname=None, output_dir='', quality='medium', **kwds):
    """
    Plots a matrix of scatterplots

       args:
          variables:
             column labels to include in scatter matrix
             
       kwds:
          alpha:
             amount of transparency applied
    
          grid:
             setting this to True will show the grid
    
          diagonal:
             'kde':  Kernel Density Estimation
        
             'hist': 20 bin Histogram
        
             None:  just labels
         
          trend :
             None:          no model fitting
        
             'linear':      f(x) = a + b*x     (default)
        
             'exponential': f(x) = a * x**b
        
             'logarithmic': f(x) = a * log(x) + b
        
             'polynomial':  f(x) = a * x**2 + b*x + c
        
             'power':       f(x) = a * x**b
        
          alternate_labels: Specifies whether the labels and ticks should
                            alternate. Default is True. When False tick labels
                            will be on the left and botttom, and variable
                            labels will be on the top and right.
    """

   # code forked from pandas.tools.plotting

    if diagonal!= None:
        if diagonal.lower() in ['hist', 'histogram']:
            diagonal = 'hist'

        if diagonal.lower() in ['kernel', 'kde']:
            diagonal = 'kde'
    else:
        diagonal = None
    
    n = len(variables)
    fig, axes = _subplots(nrows=n, ncols=n,
                          figsize=(n*2.5, n*2.5),
                          squeeze=False)

    # remove gaps between subplots
    pylab.subplots_adjust(wspace=0, hspace=0)

    ticks = {}
    lims = {}
    for a in variables:
        dmin,dmax = np.min(df[a]),np.max(df[a])
        drange = dmax-dmin
        ticks[a] = np.linspace(dmin, dmax, 5)
        lims[a] = [dmin - .1*drange, dmax + .1*drange]

    for i, a in enumerate(variables):
        for j, b in enumerate(variables):
            if i == j: # Handle cases were a == b
                if diagonal == 'hist':
                    axes[i, j].hist(df[a], 20)
                elif diagonal == 'kde':
                    y = df[a]
                    gkde = scipy.stats.gaussian_kde(y)
                    ind = np.linspace(lims[a][0], lims[a][1], 1000)
                    axes[i, j].plot(ind, gkde.evaluate(ind), alpha=.8)
                else:
                    axes[i, j].set_xlim(lims[b])
                    axes[i, j].set_ylim(lims[a])
                    axes[i, j].text(ticks[b][2], ticks[a][2], a,
                                    fontsize=14,
                                    horizontalalignment='center',
                                    verticalalignment='center')
     
                axes[i, j].set_xlim(lims[b])
                axes[i, j].set_xticks(ticks[b])
                
                # with an odd number of variables faking the y-axis
                # takes a little bit of algebra
                #
                # y0
                # |
                # y1
                # |
                # |
                # |
                # y2
                # |
                # y3
                #
                # y1 and x2 are where we want the bottom and top ticks
                # for subplots on the row y1 and y2 coorespond to the min
                # and max values
                #
                # y0 = y1-(y2-y1)*.1
                # y3 = y2+(y2-y1)*.1
                [y0,y3] = axes[i, j].get_ylim()
                y1 = y0 + .1*(y3-y0)/1.2
                y2 = y1 +    (y3-y0)/1.2
                axes[i, j].set_yticks(np.linspace(y1, y2, 5))

                if (alternate_labels and i == n-1 and n%2 == 1):           
                    axes[i, j].set_yticklabels(_tick_formatter(ticks[a]))
                    
                if (not alternate_labels and i == 0 and j == 0):
                    axes[i, j].set_yticklabels(_tick_formatter(ticks[a]))

                if i == n-1 and j == n-1:             
                    axes[i, j].set_xticklabels(_tick_formatter(ticks[b]))
                else:
                    axes[i, j].set_xticklabels([])
                    
            else: # Handle cases were a != b

                # perform trend fit if above diagonal and requested
                if i < j and trend in ['exponential','linear','logarithmic','log',
                                       'polynomial','power']:

                    trend_dict = _bivariate_trend_fit(df[b],df[a],trend)
                    model = trend_dict['model']
                    model_str = model.__doc__
                    tex_str = model_str + '\n' + r'$R^{2}=%.04f$'%trend_dict['r2']
                    
                    # plot results                      
                    ind = np.linspace(lims[b][0], lims[b][1], 1000)  
                    axes[i, j].scatter(df[b], df[a], alpha=alpha*.5, **kwds)
                    axes[i, j].plot(ind, model(ind), alpha=.8)                        
                    axes[i, j].text(ticks[b][0], ticks[a][-1],
                                    tex_str,
                                    horizontalalignment='left',
                                    verticalalignment='top',
                                    fontsize=10)
                else:
                    axes[i, j].scatter(df[b], df[a], alpha=alpha, **kwds)
                    
                axes[i, j].set_xlim(lims[b])
                axes[i, j].set_ylim(lims[a])
                axes[i, j].set_xticks(ticks[b])
                axes[i, j].set_yticks(ticks[a])
                axes[i, j].set_xticklabels(_tick_formatter(ticks[b]))
                axes[i, j].set_yticklabels(_tick_formatter(ticks[a]))
                axes[i, j].set_xlabel('')
                axes[i, j].set_ylabel('')

##                is_datetype = ticks.inferred_type in ('datetime', 'date',
##                                                  'datetime64')
##
##                if ticks.is_numeric() or is_datetype:
##                    """
##                    Matplotlib supports numeric values or datetime objects as
##                    xaxis values. Taking LBYL approach here, by the time
##                    matplotlib raises exception when using non numeric/datetime
##                    values for xaxis, several actions are already taken by plt.
##                    """
##                    ticks = ticks._mpl_repr()
                
            if alternate_labels:
                # Handle xticks and xlabels
                if i == 0: # top row
                    if j % 2 == 1:
                        axes[i, j].xaxis.set_ticks_position('top')
                    else:
                        axes[i, j].set_xticklabels([])
                        if diagonal in ['hist', 'kde']:
                            axes[i, j].set_xlabel(b)
                            axes[i, j].xaxis.set_label_position('top')
                elif i == n-1: # bottom row
                    if j % 2 == 0:
                        axes[i, j].xaxis.set_ticks_position('bottom')
                    else:
                        axes[i, j].set_xticklabels([])
                        if diagonal in ['hist', 'kde']:
                            axes[i, j].set_xlabel(b)
                            axes[i, j].xaxis.set_label_position('bottom')
                else: # middle row
                    axes[i, j].set_xticklabels([])
     
                # Handle yticks and ylabels
                if j == 0: # left column
                    if i % 2 == 1:
                        axes[i, j].yaxis.set_ticks_position('left')
                    else:
                        axes[i, j].set_yticklabels([])
                        if diagonal in ['hist', 'kde']:
                            axes[i, j].set_ylabel(a)
                            axes[i, j].yaxis.set_label_position('left')
                elif j == n-1: # right column
                    if i % 2 == 0:
                        axes[i, j].yaxis.set_ticks_position('right')
                    else:
                        axes[i, j].set_yticklabels([])
                        if diagonal in ['hist', 'kde']:
                            axes[i, j].set_ylabel(a)
                            axes[i, j].yaxis.set_label_position('right')
                else: # middle column
                    axes[i, j].set_yticklabels([])
                    
            # don't alternate labels  
            else: 
                if i == 0: # top row has xlabels
                    axes[i, j].set_xticklabels([])
                    if diagonal in ['hist', 'kde']:
                        axes[i, j].set_xlabel(b)
                        axes[i, j].xaxis.set_label_position('top')
                elif i == n-1: # bottom row has xticklabels
                    axes[i, j].xaxis.set_ticks_position('bottom')
                    
                else: # middle row
                    axes[i, j].set_xticklabels([])
     
                # Handle yticks and ylabels
                if j == 0: # left column has yticklabels
                    axes[i, j].yaxis.set_ticks_position('left')
                elif j == n-1: # right column has ylabels
                    axes[i, j].set_yticklabels([])
                    if diagonal in ['hist', 'kde']:
                        axes[i, j].set_ylabel(a)
                        axes[i, j].yaxis.set_label_position('right')
                else: # middle column
                    axes[i, j].set_yticklabels([])
                 
            labels = axes[i, j].get_xticklabels() 
            for label in labels: 
                label.set_rotation(40) 

            axes[i, j].grid(b=grid)

    if fname == None:
        fname = 'scatter_matrix('
        fname += '_X_'.join([str(f) for f in variables])
        if diagonal != None:
            fname += ',diagonal=' + diagonal
        if not alternate_labels:
            fname += ',alternate_labels=False'
        fname += ').png'

    fname = os.path.join(output_dir, fname)
        
    if quality == 'low' or fname.endswith('.svg'):
        fig.savefig(fname)
        
    elif quality == 'medium':
        fig.savefig(fname, dpi=200)
        
    elif quality == 'high':
        fig.savefig(fname, dpi=300)
        
    else:
        fig.savefig(fname)

    pylab.close()

