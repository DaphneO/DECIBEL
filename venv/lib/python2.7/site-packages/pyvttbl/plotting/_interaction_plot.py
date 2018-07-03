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
import math

from collections import Counter
from copy import copy, deepcopy

import pylab
import scipy
import numpy as np

from pyvttbl.misc.support import _isfloat,_str

def interaction_plot(df, val, xaxis, 
                     seplines=None, sepxplots=None, sepyplots=None,
                     xmin='AUTO', xmax='AUTO', ymin='AUTO', ymax='AUTO',
                     where=None, fname=None, output_dir='',
                     quality='low', yerr=None):
    """
    makes an interaction plot

       args:
          df:
             a pyvttbl.DataFrame object
    
          val:
             the label of the dependent variable
    
          xaxis:
             the label of the variable to place on the xaxis of each subplot

       kwds:
          seplines:
             label specifying seperate lines in each subplot
               
          sepxplots:
             label specifying seperate horizontal subplots
                
          sepyplots:
             label specifying separate vertical subplots
                
          xmin:
             ('AUTO' by default) minimum xaxis value across subplots
    
          xmax:
             ('AUTO' by default) maximum xaxis value across subplots
    
          ymin:
             ('AUTO' by default) minimum yaxis value across subplots
    
          ymax:
             ('AUTO' by default) maximum yaxis value across subplots
    
          where:
             a string, list of strings, or list of tuples
             applied to the DataFrame before plotting
            
          fname:
             output file name
    
          quality:
             {'low' | 'medium' | 'high'} specifies image file dpi
    
          yerr:
             {float, 'ci', 'stdev', 'sem'} designates errorbars across
             datapoints in all subplots
    """

    ##############################################################
    # interaction_plot programmatic flow                         #
    ##############################################################
    #  1. Check to make sure a plot can be generated with the    # 
    #     specified arguments and parameter                      #
    #  2. Set yerr aggregate                                     #
    #  3. Figure out ymin and ymax if 'AUTO' is specified        #
    #  4. Figure out how many subplots we need to make and the   #
    #     levels of those subplots                               #
    #  5. Initialize pylab.figure and set plot parameters        #
    #  6. Build and set main title                               #
    #  7. loop through the the rlevels and clevels and make      #
    #     subplots                                               #
    #      7.1 Create new axes for the subplot                   #
    #      7.2 Add subplot title                                 #
    #      7.3 Format the subplot                                #
    #      7.4 Iterate plotnum counter                           #
    #  8. Place yerr text in bottom right corner                 #
    #  9. Save the figure                                        #
    # 10. return the test dictionary                             #
    ##############################################################

    #  1. Check to make sure a plot can be generated with the    
    #     specified arguments and parameter
    ##############################################################
    # pylab doesn't like not being closed. To avoid starting
    # a plot without finishing it, we do some extensive checking
    # up front

    if where == None:
        where = []

    # check for data
    if df == {}:
        raise Exception('Table must have data to plot marginals')

    # check to see if data columns have equal lengths
    if not df._are_col_lengths_equal():
        raise Exception('columns have unequal lengths')

    # check to make sure arguments are column labels
    if val not in df.keys():
        raise KeyError(val)

    if xaxis not in df.keys():
        raise KeyError(xaxis)
    
    if seplines not in df.keys() and seplines != None:
        raise KeyError(seplines)

    if sepxplots not in df.keys() and sepxplots != None:
        raise KeyError(sepxplots)
    
    if sepyplots not in df.keys() and sepyplots != None:
        raise KeyError(sepyplots)

    # check for duplicate names
    dup = Counter([val, xaxis, seplines, sepxplots, sepyplots])
    del dup[None]
    if not all([count == 1 for count in dup.values()]):
        raise Exception('duplicate labels specified as plot parameters')

    # check fname
    if not isinstance(fname, _strobj) and fname != None:
        raise TypeError('fname must be None or string')

    if isinstance(fname, _strobj):
        if not (fname.lower().endswith('.png') or \
                fname.lower().endswith('.svg')):
            raise Exception('fname must end with .png or .svg')                

    # check cell counts
    cols = [f for f in [seplines, sepxplots, sepyplots] if f in df.keys()]
    counts = df.pivot(val, rows=[xaxis], cols=cols,
                      where=where, aggregate='count')

    # unpack conditions DictSet from counts PyvtTbl
    # we need to do it this way instead of using df.conditions
    # because the counts PyvtTbl reflects the where exclusions
    conditions = counts.conditions

    # flatten counts to MaskedArray
    counts = counts.flatten()

    for count in counts:
        if count < 1:
            raise Exception('cell count too low to calculate mean')

    #  2. Initialize test dictionary
    ##############################################################
    # To test the plotting a dict with various plot parameters
    # is build and returned to the testing module. In this
    # scenario our primary concern is that the values represent
    # what we think they represent. Whether they match the plot
    # should be fairly obvious to the user. 
    test = {}
    
    #  3. Set yerr aggregate so sqlite knows how to calculate yerr
    ##############################################################
    
    # check yerr
    aggregate = None
    if yerr == 'sem':
        aggregate = 'sem'
        
    elif yerr == 'stdev':
        aggregate = 'stdev'
        
    elif yerr == 'ci':
        aggregate = 'ci'

    for count in counts:
        if aggregate != None and count < 2:
            raise Exception('cell count too low to calculate %s'%yerr)

    test['yerr'] = yerr
    test['aggregate'] = aggregate

    #  4. Figure out ymin and ymax if 'AUTO' is specified
    ##############################################################            
    desc = df.descriptives(val)
    
    if ymin == 'AUTO':
        # when plotting postive data always have the y-axis go to 0
        if desc['min'] >= 0.:
            ymin = 0. 
        else:
            ymin = desc['mean'] - 3.*desc['stdev']
    if ymax == 'AUTO':
        ymax = desc['mean'] + 3.*desc['stdev']

    if any([math.isnan(ymin), math.isinf(ymin), math.isnan(ymax), math.isinf(ymax)]):
        raise Exception('calculated plot bounds nonsensical')

    test['ymin'] = ymin
    test['ymax'] = ymax

    #  5. Figure out how many subplots we need to make and the
    #     levels of those subplots
    ##############################################################      
    numrows = 1
    rlevels = [1]
    if sepyplots != None:
        rlevels = copy(conditions[sepyplots]) # a set
        numrows = len(rlevels) # a int
        rlevels = sorted(rlevels) # set -> sorted list
            
    numcols = 1
    clevels = [1]            
    if sepxplots != None:
        clevels = copy(conditions[sepxplots])
        numcols = len(clevels)
        clevels = sorted(clevels) # set -> sorted list

    test['numrows']  = numrows
    test['rlevels']  = rlevels
    test['numcols']  = numcols
    test['clevels']  = clevels
    
    #  6. Initialize pylab.figure and set plot parameters
    ##############################################################  
    fig = pylab.figure(figsize=(6*numcols, 4*numrows+1))
    fig.subplots_adjust(wspace=.05, hspace=0.2)
    
    #  7. Build and set main title
    ##############################################################  
    maintitle = '%s by %s'%(val,xaxis)
    
    if seplines:
        maintitle += ' * %s'%seplines
    if sepxplots:
        maintitle += ' * %s'%sepxplots
    if sepyplots:
        maintitle += ' * %s'%sepyplots
        
    fig.text(0.5, 0.95, maintitle,
             horizontalalignment='center',
             verticalalignment='top')

    test['maintitle']  = maintitle
    
    #  8. loop through the the rlevels and clevels and make
    #     subplots
    ##############################################################
    test['y'] = []
    test['yerr'] = []
    test['subplot_titles'] = []
    test['xmins'] = []
    test['xmaxs'] = []
    
    plotnum = 1 # subplot counter
    axs = []

    for r, rlevel in enumerate(rlevels):
        for c, clevel in enumerate(clevels):
            where_extension = []
            if sepxplots!=None:
                where_extension.append((sepxplots, '=', [clevel]))
            if sepyplots!=None:
                where_extension.append((sepyplots, '=', [rlevel]))
            
            #  8.1 Create new axes for the subplot
            ######################################################
            axs.append(pylab.subplot(numrows, numcols, plotnum))

            ######## If separate lines are not specified #########
            if seplines == None:
                y = df.pivot(val, cols=[xaxis],
                               where=where+where_extension,
                               aggregate='avg')
                
                cnames = y.cnames
                y = y.flatten()

                if aggregate != None:
                    yerr = df.pivot(val, cols=[xaxis],
                                      where=where+where_extension,
                                      aggregate=aggregate).flatten()
                
                x = [name for [(label, name)] in cnames]
                
                if _isfloat(yerr):
                    yerr = np.array([yerr for a in x])

                if all([_isfloat(a) for a in x]):
                    axs[-1].errorbar(x, y, yerr)
                    if xmin == 'AUTO' and xmax == 'AUTO':
                        xmin, xmax = axs[-1].get_xlim()
                        xran = xmax - xmin
                        xmin = xmin - 0.05*xran
                        xmax = xmax + 0.05*xran

                    axs[-1].plot([xmin, xmax], [0., 0.], 'k:')
                    
                else : # categorical x axis
                    axs[-1].errorbar(_xrange(len(x)), y, yerr)
                    pylab.xticks(_xrange(len(x)), x)
                    xmin = - 0.5
                    xmax = len(x) - 0.5
                    
                    axs[-1].plot([xmin, xmax], [0., 0.], 'k:')

            ########## If separate lines are specified ###########
            else:                       
                y = df.pivot(val, rows=[seplines], cols=[xaxis],
                               where=where+where_extension,
                               aggregate='avg')
                
                if aggregate != None:
                    yerrs = df.pivot(val,
                                       rows=[seplines],
                                       cols=[xaxis],
                                       where=where+where_extension,
                                       aggregate=aggregate)
                    
                x = [name for [(label, name)] in y.cnames]

                if _isfloat(yerr):
                    yerr = np.array([yerr for a in x])

                plots = []
                labels = []
                for i, name in enumerate(y.rnames):
                    if aggregate != None:
                        yerr = yerrs[i].flatten()
                    
                    labels.append(name[0][1])

                    if all([_isfloat(a) for a in x]):
                        plots.append(
                            axs[-1].errorbar(x, y[i].flatten(), yerr)[0])
                        
                        if xmin == 'AUTO' and xmax == 'AUTO':
                            xmin , xmax = axs[-1].get_xlim()
                            xran = xmax - xmin
                            xmin = xmin - .05*xran
                            xmax = xmax + .05*xran
                            
                        axs[-1].plot([xmin, xmax], [0.,0.], 'k:')
                        
                    else : # categorical x axis
                        plots.append(
                            axs[-1].errorbar(
                                _xrange(len(x)), y[i].flatten(), yerr)[0])
                        
                        pylab.xticks(_xrange(len(x)), x)
                        xmin = - 0.5
                        xmax = len(x) - 0.5
                        
                        axs[-1].plot([xmin, xmax], [0., 0.], 'k:')

                pylab.figlegend(plots, labels, loc=1,
                                labelsep=.005,
                                handlelen=.01,
                                handletextsep=.005)

            test['y'].append(y)
            if yerr == None:
                test['yerr'].append([])
            else:
                test['yerr'].append(yerr)
            test['xmins'].append(xmin)
            test['xmaxs'].append(xmax)

            #  8.2 Add subplot title
            ######################################################
            if rlevels == [1] and clevels == [1]:
                title = ''
                
            elif rlevels == [1]:
                title = _str(clevel)
                
            elif clevels == [1]:
                title = _str(rlevel)
                
            else:
                title = '%s = %s, %s = %s' \
                        % (sepyplots, _str(rlevel),
                           sepxplots, _str(rlevel))
                
            pylab.title(title, fontsize='medium')
            test['subplot_titles'].append(title)

            #  8.3 Format the subplot
            ######################################################
            pylab.xlim(xmin, xmax)
            pylab.ylim(ymin, ymax)

            # supress tick labels unless subplot is on the bottom
            # row or the far left column
            if r != (len(rlevels) - 1):
                pylab.setp(axs[-1].get_xticklabels(), visible=False)
                
            if c != 0:
                pylab.setp(axs[-1].get_yticklabels(), visible=False)

            # Set the aspect ratio for the subplot
            Dx = abs(axs[-1].get_xlim()[0] - axs[-1].get_xlim()[1])
            Dy = abs(axs[-1].get_ylim()[0] - axs[-1].get_ylim()[1])
            axs[-1].set_aspect(.75*Dx/Dy)
            
            #  8.4 Iterate plotnum counter
            ######################################################
            plotnum += 1

    #  9. Place yerr text in bottom right corner
    ##############################################################
    if aggregate != None:
        if aggregate == 'ci':
            aggregate = '95% ci' 
            
        pylab.xlabel('\n\n                '
                     '*Error bars reflect %s'\
                     %aggregate.upper())

    # 10. Save the figure
    ##############################################################
    if fname == None:
        fname = 'interaction_plot(%s'%val
        factors = [xaxis,seplines,sepxplots,sepyplots]
        fname += '~' + '_X_'.join([str(f) for f in factors if f != None])
        if aggregate != None:
            fname += ',yerr=' + aggregate
        elif yerr != None:
            fname += ',yerr=' + str(yerr[0])
        fname += ').png'

    fname = os.path.join(output_dir, fname)
    
    if quality == 'low' or fname.endswith('.svg'):
        pylab.savefig(fname)
        
    elif quality == 'medium':
        pylab.savefig(fname, dpi=200)
        
    elif quality == 'high':
        pylab.savefig(fname, dpi=300)
        
    else:
        pylab.savefig(fname)

    pylab.close()

    test['fname'] = fname

    # 11. return the test dictionary
    ##############################################################
    if df.TESTMODE:
        return test
