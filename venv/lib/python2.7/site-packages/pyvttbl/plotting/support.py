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

import numpy as np
import scipy
import matplotlib.pyplot as plt

from pyvttbl.misc.texttable import _str
        
def _bivariate_trend_fit(x,y,trend):
    x,y = np.array(x),np.array(y)

    # build fit function
    if   trend == 'exponential':
        fitfunc_str = 'p[0]*np.exp(p[1]*x)'
    elif trend == 'linear':
        fitfunc_str = 'p[0]+p[1]*x'
    elif trend in ['log', 'logarithmic']:
        fitfunc_str = 'p[0]*np.log(x)+p[1]'
    elif trend == 'polynomial':
        fitfunc_str = 'p[0]*x**2 + p[1]*x + p[2]'
    elif trend == 'power':
        fitfunc_str = 'p[0]*x**p[1]'
    fitfunc = eval('lambda p, x : %s'%fitfunc_str)

    # build error function
    errfunc = lambda p, x, y: y - fitfunc(p, x)

    pinit = [1.0, -.1]
    out = scipy.optimize.leastsq(errfunc, pinit,
                                 args=(x, y),
                                 full_output=1)
    pfinal = out[0]
    covar = out[1]

    a = pfinal[1]
    k = pfinal[0]

    # manual calculate r^2, F, p
    y_bar = np.mean(y)
    y_hat = fitfunc(pfinal, x)

    ssm = np.sum([(_y-y_bar)**2 for _y in y_hat])
    sst = np.sum([(_y-y_bar)**2 for _y in y])
    sse = sst - ssm

    r2 = 1. - sse/sst
    F = ssm / sse

    n = len(x)
    dfm = 1
    dfe = n - 2
    dft = n - 1

    p = scipy.stats.f(dfm,dfe).sf(F)

    # build model string for best fit
    if   trend == 'exponential':
        model_str = r'$y=%.3f \exp(%.3fx)$'%tuple(pfinal)
    elif trend == 'linear':
        model_str = r'$y=%.3f +%.3fx$'%tuple(pfinal)
    elif trend in ['log', 'logarithmic']:
        model_str = r'$y=%.3f \ln(x) +%.3f$'%tuple(pfinal)
    elif trend == 'polynomial':
        model_str = r'$y=%.3fx^2 +%.3fx +%.3f$'%tuple(pfinal)
    elif trend == 'power':
        model_str = r'$y=%.3fx^{%.3f}$'%tuple(pfinal)
    model_str = model_str.replace('+-','-')

    model = lambda x : fitfunc(pfinal,x)
    model.__doc__ = model_str
    
    return dict(zip('model coeffs r2 F p ssm sse sst dfm dfe dft'.split(),
                    [model, pfinal, r2, F, p, ssm, sse, sst, dfm, dfe, dft]))

def _tick_formatter(ticks):
    return [_str(t) for t in ticks]
    
##    # this could be tweaked more.
##    # I didn't spend alot of time with it.
##    s = [len(str(round(t,0)).replace('.0','').replace('.','')) for t in ticks]
##
##    # all integers less than 1,000,000
##    if all([(int(t)-t) == 0 for t in ticks]) and all([c<8 for c in s]):
##        return ['%i'%t for t in ticks]
##
##    # all less than 10
##    if max(s) == 1:
##        # all really small
##        if any([t<.00001 for t in ticks]):            
##            return ['%.1e'%t for t in ticks]
##        return ['%.4f'%t for t in ticks]
##
##    # contains at least 1 "big" number
##    if any([c>=8 for c in s]):
##        return ['%.1e'%t for t in ticks]
##
##    # between 10 and 1,000,000
##    else:
##        return ['%i'%int(round(t)) for t in ticks]

# copied from matplotlib/pyplot.py for compatibility with matplotlib < 1.0
def _subplots(nrows=1, ncols=1, sharex=False, sharey=False, squeeze=True,
              subplot_kw=None, ax=None, **fig_kw):
    """Create a figure with a set of subplots already made.

    This utility wrapper makes it convenient to create common layouts of
    subplots, including the enclosing figure object, in a single call.

    Keyword arguments:

    nrows : int
      Number of rows of the subplot grid.  Defaults to 1.

    ncols : int
      Number of columns of the subplot grid.  Defaults to 1.

    sharex : bool
      If True, the X axis will be shared amongst all subplots.

    sharex : bool
      If True, the Y axis will be shared amongst all subplots.

    squeeze : bool

      If True, extra dimensions are squeezed out from the returned axis object:
        - if only one subplot is constructed (nrows=ncols=1), the resulting
        single Axis object is returned as a scalar.
        - for Nx1 or 1xN subplots, the returned object is a 1-d numpy object
        array of Axis objects are returned as numpy 1-d arrays.
        - for NxM subplots with N>1 and M>1 are returned as a 2d array.

      If False, no squeezing at all is done: the returned axis object is always
      a 2-d array contaning Axis instances, even if it ends up being 1x1.

    subplot_kw : dict
      Dict with keywords passed to the add_subplot() call used to create each
      subplots.

    fig_kw : dict
      Dict with keywords passed to the figure() call.  Note that all keywords
      not recognized above will be automatically included here.

    ax : Matplotlib axis object, default None

    Returns:

    fig, ax : tuple
      - fig is the Matplotlib Figure object
      - ax can be either a single axis object or an array of axis objects if
      more than one supblot was created.  The dimensions of the resulting array
      can be controlled with the squeeze keyword, see above.

    **Examples:**

    x = np.linspace(0, 2*np.pi, 400)
    y = np.sin(x**2)

    # Just a figure and one subplot
    f, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_title('Simple plot')

    # Two subplots, unpack the output array immediately
    f, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
    ax1.plot(x, y)
    ax1.set_title('Sharing Y axis')
    ax2.scatter(x, y)

    # Four polar axes
    plt.subplots(2, 2, subplot_kw=dict(polar=True))
    """

    if subplot_kw is None:
        subplot_kw = {}

    if ax is None:
        fig = plt.figure(**fig_kw)
    else:
        fig = ax.get_figure()
        fig.clear()

    # Create empty object array to hold all axes.  It's easiest to make it 1-d
    # so we can just append subplots upon creation, and then
    nplots = nrows*ncols
    axarr = np.empty(nplots, dtype=object)

    # Create first subplot separately, so we can share it if requested
    ax0 = fig.add_subplot(nrows, ncols, 1, **subplot_kw)
    if sharex:
        subplot_kw['sharex'] = ax0
    if sharey:
        subplot_kw['sharey'] = ax0
    axarr[0] = ax0

    # Note off-by-one counting because add_subplot uses the MATLAB 1-based
    # convention.
    for i in range(1, nplots):
        axarr[i] = fig.add_subplot(nrows, ncols, i+1, **subplot_kw)

    if nplots > 1:
        if sharex and nrows > 1:
            for i, ax in enumerate(axarr):
                if np.ceil(float(i + 1) / ncols) < nrows: # only last row
                    [label.set_visible(False) for label in ax.get_xticklabels()]
        if sharey and ncols > 1:
            for i, ax in enumerate(axarr):
                if (i % ncols) != 0: # only first column
                    [label.set_visible(False) for label in ax.get_yticklabels()]

    if squeeze:
        # Reshape the array to have the final desired dimension (nrow,ncol),
        # though discarding unneeded dimensions that equal 1.  If we only have
        # one subplot, just return it instead of a 1-element array.
        if nplots==1:
            axes = axarr[0]
        else:
            axes = axarr.reshape(nrows, ncols).squeeze()
    else:
        # returned axis array will be always 2-d, even if nrows=ncols=1
        axes = axarr.reshape(nrows, ncols)

    return fig, axes

