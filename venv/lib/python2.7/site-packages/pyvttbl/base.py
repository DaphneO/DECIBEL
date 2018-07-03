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

import collections
import csv
import itertools
import inspect
import math
import sqlite3
import warnings

from pprint import pprint as pp
from copy import copy, deepcopy
from collections import OrderedDict, Counter, namedtuple

import pylab
import scipy
import numpy as np

import pystaggrelite3
from dictset import DictSet

import stats
from stats.qsturng import qsturng, psturng
from misc.texttable import Texttable as TextTable
from misc.support import *
import plotting

# base.py holds DataFrame and Pyvttbl
# this file is a bit long but they can't be split without
# running into circular import complications

class DataFrame(OrderedDict):
    """holds the data in a dummy-coded group format"""
    def __init__(self, *args, **kwds):
        """
        initialize a :class:`DataFrame` object.

        |   Subclass of :mod:`collections`. :class:`OrderedDict`.           
        |   Understands the typical initialization :class:`dict` signatures.
        |   Keys must be hashable.
        |   Values become numpy.arrays or numpy.ma.MaskedArrays.
           
        """
        super(DataFrame, self).__init__()
        
        #: sqlite3 connection
        self.conn = sqlite3.connect(':memory:')
        
        #: sqlite3 cursor
        self.cur = self.conn.cursor()
        
        #: list of sqlite3 aggregates
        self.aggregates = tuple('avg count count group_concat '  \
                                'group_concat max min sum total tolist' \
                                .split())

        # Bind pystaggrelite3 aggregators to sqlite3
        for n, a, f in pystaggrelite3.getaggregators():
            self.bind_aggregate(n, a, f)

        #: prints the sqlite3 queries to stdout before
        #: executing them for debugging purposes
        self.PRINTQUERIES = False

        #: controls whether plot functions return the test dictionaries
        self.TESTMODE = False

        #: holds the factors conditions in a DictSet Singleton
        self.conditions = DictSet()

        #: dict to map keys to sqlite3 types
        self._sqltypesdict = {}

        super(DataFrame, self).update(*args, **kwds)

    def bind_aggregate(self, name, arity, func):
        """
        binds a sqlite3 aggregator to :class:`DataFrame`

           args:
              name: string to be associated with the aggregator
              
              arity: the number of inputs required by the aggregator
              
              func: the aggregator class

           returns:
              None
              
        |   :class:`DataFrame`.aggregates is a list of the available aggregators.
        |   For information on rolling your own aggregators see:
            http://docs.python.org/library/sqlite3.html
        """
        self.conn.create_aggregate(name, arity, func)
        
        self.aggregates = list(self.aggregates)
        self.aggregates.append(name)
        self.aggregates = tuple(self.aggregates)

    def _get_sqltype(self, key):
        """
        returns the sqlite3 type associated with the provided key

           args:
              key: key in :class:`DataFrame` (raises KeyError if key not in self)

           returns:
              a string specifiying the sqlite3 type associated with the data in self[key]:
                 { 'null', 'integer', 'real', 'text'}
        """
        return self._sqltypesdict[key]
                       
    def _get_nptype(self, key):
        """
        returns the numpy type object associated with the provided key

           args:
              key: key in :class:`DataFrame` (raises KeyError if key not in self)

           returns:
              a numpy object specifiying the type associated with the data in self[key]:

                 =========   ================
                 sql type    numpy type
                 =========   ================
                 'null'      np.dtype(object)
                 'integer'   np.dtype(int)
                 'real'      np.dtype(float)
                 'text'      np.dtype(str)
                 =========   ================
        """
        return {'null' : np.dtype(object),
                'integer' : np.dtype(int),
                'real' : np.dtype(float),
                'text' : np.dtype(str)}[self._sqltypesdict[key]]
    
    def _get_mafillvalue(self, key):

        """
        returns the default fill value for invalid data associated with the provided key.

           args:
              key: key in :class:`DataFrame` (raises KeyError if key not in self)

           returns:
              string, float, or int associated with the data in self[key]
              
                 =========   ============
                 sql type    default
                 =========   ============
                 'null'      '?'
                 'integer'   999999
                 'real'      1e20
                 'text'      'N/A'
                 =========   ============
        
        |   returned values match the defaults associated with np.ma.MaskedArray
        """
        return {'null' : '?',
                'integer' : 999999,
                'real' : 1e20,
                'text' : 'N/A'}[self._sqltypesdict[key]]

    def read_tbl(self, fname, skip=0, delimiter=',',labels=True):
        """
        loads tabulated data from a plain text file
        
           args:
              fname: path and name of datafile

           kwds:
              skip: number of lines to skip before looking for column labels. (default = 0)
              
              delimiter: string to seperate values (default = "'")
              
              labels: bool specifiying whether first row (after skip) contains labels.
              (default = True)
              
           returns:
              None
              
        |   Checks and renames duplicate column labels as well as checking
        |   for missing cells. readTbl will warn and skip over missing lines.
        """
        
        # open and read dummy coded data results file to data dictionary
        fid = open(fname, 'r')
        csv_reader = csv.reader(fid, delimiter=delimiter)
        data = OrderedDict()
        mask = {}
        colnames = []
        
        for i, row in enumerate(csv_reader):
            # skip requested rows
            if i < skip:
                pass
            
            # read column labels from ith+1 line
            elif i == skip and labels:
                colnameCounter = Counter()
                for k, colname in enumerate(row):
                    colname = colname.strip()#.replace(' ','_')
                    colnameCounter[colname] += 1
                    if colnameCounter[colname] > 1:
                        warnings.warn("Duplicate label '%s' found"
                                      %colname,
                                      RuntimeWarning)
                        colname += '_%i'%colnameCounter[colname]                   
                    colnames.append(colname)
                    data[colname] = []
                    mask[colname] = []

            # if labels is false we need to make labels
            elif i == skip and not labels:
                colnames = ['COL_%s'%(k+1) for k in range(len(row))]
                for j,colname in enumerate(colnames):
                    if _isfloat(row[j]):
                        data[colname] = [float(row[j])]
                        mask[colname] = [0]
                    else:
                        data[colname] = [row[i]]
                        if row[i] == '':
                            mask[colname] = [1]
                        else:
                            mask[colname] = [0]

            # for remaining lines where i>skip...
            else:
                if len(row) != len(colnames):
                    warnings.warn('Skipping line %i of file. '
                                  'Expected %i cells found %i'\
                                  %(i+1, len(colnames), len(row)),
                                  RuntimeWarning)
                else:                    
                    for j, colname in enumerate(colnames):                        
                        colname = colname.strip()
                        if _isfloat(row[j]):
                            data[colname].append(float(row[j]))
                            mask[colname].append(0)
                        else:
                            data[colname].append(row[j])
                            if row[j] == '':
                                mask[colname].append(1)
                            else:
                                mask[colname].append(0)
            
        # close data file
        fid.close()
        self.clear()
        for k, v in data.items():
            ## In __setitem__ the conditions DictSet and datatype are set 
            self.__setitem__(k, v, mask[k])
            
        del data

    def __setitem__(self, key, item, mask=None):
        """
        assign a column in the table
        
           args:
              key: hashable object to associate with item

              item: an iterable that is put in an np.array or np.ma.array

           kwds:
              mask: mask value passed to np.ma.MaskedArray.__init__()
              
           returns:
              None
              
        |   df.__setitem__(key, item) <==> df[key] = item
        
        |   The assigned item must be iterable. To add a single row use
            the insert method. To  another table to this one use
            the attach method.

           example:
              >>> ...
              >>> print(df)
              first      last       age   gender 
              ==================================
              Roger   Lew            28   male   
              Bosco   Robinson        5   male   
              Megan   Whittington    26   female 
              John    Smith          51   male   
              Jane    Doe            49   female 
              >>> import numpy as np
              >>> df['log10(age)'] = np.log10(df['age'])
              >>> print(df)
              first      last       age   gender   log10(age) 
              ===============================================
              Roger   Lew            28   male          1.447 
              Bosco   Robinson        5   male          0.699 
              Megan   Whittington    26   female        1.415 
              John    Smith          51   male          1.708 
              Jane    Doe            49   female        1.690 
              >>> 
        """
        
        # check item
        if not hasattr(item, '__iter__'):
            raise TypeError("'%s' object is not iterable"%type(item).__name__)
        
        if key in self.keys():
            del self[key]

        # a mask was provided
        if mask != None:
            # data contains invalid entries and a masked array should be created
            # this needs to be nested incase mask != None
            if not all([m==0 for m in mask]):

                # figure out the datatype of the valid entries
                self._sqltypesdict[key] = \
                    self._determine_sqlite3_type([d for d,m in zip(item,mask) if not m])

                # replace invalid values
                fill_val = self._get_mafillvalue(key)
                x = np.array([(d, fill_val)[m] for d,m in zip(item,mask)])
                
                # call super.__setitem__
                super(DataFrame, self).\
                    __setitem__(key, \
                        np.ma.array(x, mask=mask, dtype=self._get_nptype(key)))

                # set or update self.conditions DictSet
                self.conditions[key] = self[key]

                # return if successful
                return

        # no mask provided or mask is all true
        self._sqltypesdict[key] = self._determine_sqlite3_type(item)
        super(DataFrame, self).\
            __setitem__(key, np.array(item, dtype=self._get_nptype(key)))
            
        self.conditions[key] = self[key]

##    def __iter__(self):
##        raise NotImplementedError('use .keys() to iterate')
        
    def __delitem__(self, key):
        """
        delete a column from the table
        
           args:
              key: associated with the item to delete
              
           returns:
              None
              
        |   df.__delitem__(key) <==> del df[key]

           example:
              >>> ...
              >>> print(df)
              first      last       age   gender   log10(age) 
              ===============================================
              Roger   Lew            28   male          1.447 
              Bosco   Robinson        5   male          0.699 
              Megan   Whittington    26   female        1.415 
              John    Smith          51   male          1.708 
              Jane    Doe            49   female        1.690 
              >>> del df['log10(age)']
              >>> print(df)
              first      last       age   gender 
              ==================================
              Roger   Lew            28   male   
              Bosco   Robinson        5   male   
              Megan   Whittington    26   female 
              John    Smith          51   male   
              Jane    Doe            49   female 
              >>> 
        """

        del self._sqltypesdict[key]
        del self.conditions[key]
        super(DataFrame, self).__delitem__(key)
        
    def __str__(self):
        """
        returns human friendly string representation of object

           args:
              None
              
           returns:
              string with easy to read representation of table

        |   df.__str__() <==> str(df)
        """
        if self == {}:
            return '(table is empty)'
        
        tt = TextTable(max_width=100000000)
        dtypes = [t[0] for t in self.types()]
        dtypes = list(''.join(dtypes).replace('r', 'f'))
        tt.set_cols_dtype(dtypes)

        aligns = [('l','r')[dt in 'fi'] for dt in dtypes]
        tt.set_cols_align(aligns)
        
        tt.header(self.keys())
        if self.shape()[1] > 0:
            tt.add_rows(zip(*list(self.values())), header=False)
        tt.set_deco(TextTable.HEADER)

        # output the table
        return tt.draw()

    def row_iter(self):
        """
        iterate over the rows in table

           args:
              None

           returns:
              iterator that yields OrderedDict objects with (key,value) pairs
              cooresponding to the data in each row

           example:
              >>> print(df)
              first      last       age   gender 
              ==================================
              Roger   Lew            28   male   
              Bosco   Robinson        5   male   
              Megan   Whittington    26   male   
              John    Smith          51   female 
              Jane    Doe            49   female 
              >>> for case in df.row_iter():
                      print(case)
              OrderedDict([('first', 'Roger'), ('last', 'Lew'), ('age', 28), ('gender', 'male')])
              OrderedDict([('first', 'Bosco'), ('last', 'Robinson'), ('age', 5), ('gender', 'male')])
              OrderedDict([('first', 'Megan'), ('last', 'Whittington'), ('age', 26), ('gender', 'male')])
              OrderedDict([('first', 'John'), ('last', 'Smith'), ('age', 51), ('gender', 'female')])
              OrderedDict([('first', 'Jane'), ('last', 'Doe'), ('age', 49), ('gender', 'female')])
              >>> 
"""
        for i in _xrange(self.shape()[1]):
            yield OrderedDict([(k, self[k][i]) for k in self])
        
    def types(self):
        """
        returns a list of the sqlite3 datatypes of the columns 
           args:
              None
              
           returns:
              an ordered list of sqlite3 types.

        |   order matches self.keys() 
        """
        if len(self) == 0:
            return []
        
        return [self._sqltypesdict[k] for k in self]

    def shape(self):
        """
        returns the size of the data in the table as a tuple

           args:
              None
              
           returns:
              tuple (number of columns, number of rows)
        """
        if len(self) == 0:
            return (0, 0)
        
        return (len(self), len(self.values()[0]))
    
    def _are_col_lengths_equal(self):
        """
        private method to check if the items in self have equal lengths

           args:
              None
              
           returns:
              returns True if all the items are equal
           
              returns False otherwise
        """
        if len(self) < 2:
            return True
        
        # if self is not empty
        counts = map(len, self.values())
        if all(c - counts[0] + 1 == 1 for c in counts):
            return True
        else:
            return False

    def _determine_sqlite3_type(self, iterable):
        """
        determine the sqlite3 datatype of iterable
        
           args:
              iterable: a 1-d iterable (list, tuple, np.array, etc.)
              
          returns:
              sqlite3 type as string: 'null', 'integer', 'real', or 'text'
        """
        if len(iterable) == 0:
            return 'null'
        elif all(map(_isint, iterable)):
            return 'integer'
        elif all(map(_isfloat, iterable)):
            return 'real'
        else:
            return 'text'

    def _execute(self, query, t=None):
        """
        private method to execute sqlite3 query

        |   When the PRINTQUERIES bool is true it prints the queries
            before executing them
        """
        if t == None:
            t=tuple()
            
        if self.PRINTQUERIES:
            print(query)
            if len(t) > 0:
                print('  ', t)
            print()

        self.cur.execute(query, t)

    def _executemany(self, query, tlist):
        """
        private method to execute sqlite3 queries

        |   When the PRINTQUERIES bool is true it prints the queries
            before executing them. The execute many method is about twice
            as fast for building tables as the execute method.
        """
        if self.PRINTQUERIES:
            print(query)
            print('  ', tlist[0])
            print('   ...\n')

        self.cur.executemany(query, tlist)

    def _get_indices_where(self, where):
        """
        determines the indices cooresponding to the conditions specified by the where
        argument.

           args:
              where: a string criterion without the 'where'

           returns:
              a list of indices
        """

        # preprocess where
        tokens = []
        nsubset2 = set()
        names = self.keys()
        for w in where.split():
            print(w)
            if w in names:
                tokens.append(_sha1(w))
                nsubset2.add(w)
            else:
                tokens.append(w)
        where = ' '.join(tokens)

        super(DataFrame, self).__setitem__(('INDICES','integer'),
                                         range(self.shape()[1]))
                                         
        nsubset2.add('INDICES')

        # build the table
        self.conn.commit()
        self._execute('drop table if exists GTBL')

        self.conn.commit()
        query =  'create temp table GTBL\n  ('
        query += ', '.join('%s %s'%(_sha1(n), self._get_sqltype(n)) for n in nsubset2)
        query += ')'
        self._execute(query)

        # build insert query
        query = 'insert into GTBL values ('
        query += ','.join('?' for n in nsubset2) + ')'
        self._executemany(query, zip(*[self[n] for n in nsubset2]))
        self.conn.commit()

        super(DataFrame, self).__delitem__(('INDICES','integer'))

        # get the indices
        query = 'select %s from GTBL where %s'%(_sha1('INDICES'), where)
        self._execute(query)
        

    def _build_sqlite3_tbl(self, nsubset, where=None):
        """
        build or rebuild sqlite table with columns in nsubset based on
        the where list.

           args:
              nsubset: a list of keys to include in the table

              where: criterion the entries in the table must satisfy

           returns:
              None

        |   where can be a list of tuples. Each tuple should have three
            elements. The first should be a column key (label). The second
            should be an operator: in, =, !=, <, >. The third element
            should contain value for the operator.

        |   where can also be a list of strings. or a single string.

        |   sqlite3 table is built in memory and has the id TBL
        """
        if where == None:
            where = []

        if isinstance(where, _strobj):
            where = [where]
            
        #  1. Perform some checking
        ##############################################################
        if not hasattr(where, '__iter__'):
            raise TypeError( "'%s' object is not iterable"
                             % type(where).__name__)

        #  2. Figure out which columns need to go into the table
        #     to be able to filter the data
        ##############################################################           
        nsubset2 = set(nsubset)
        for item in where:
            if isinstance(item, _strobj):
                tokens = item.split()
                if tokens[0] not in self.keys():
                    raise KeyError(tokens[0])
                nsubset2.update(w for w in tokens if w in self.keys())
            else: # tuple
                if item[0] in self.keys():
                    nsubset2.add(item[0])

        # orders nsubset2 to match the order in self.keys()
        nsubset2 = [n for n in self if n in nsubset2]

        #  3. Build a table
        ##############################################################
        self.conn.commit()
        self._execute('drop table if exists TBL2')

        self.conn.commit()
        query =  'create temp table TBL2\n  ('
        query += ', '.join('%s %s'%(_sha1(n), self._get_sqltype(n)) for n in nsubset2)
        query += ')'
        self._execute(query)

        # build insert query
        query = 'insert into TBL2 values ('
        query += ','.join('?' for n in nsubset2) + ')'

        # because sqlite3 does not understand numpy datatypes we need to recast them
        # using astype to numpy.object
        self._executemany(query, zip(*[self[n].astype(np.object) for n in nsubset2]))
        self.conn.commit()

        #  4. If where == None then we are done. Otherwise we need
        #     to build query to filter the rows
        ##############################################################
        if where == []:
            self._execute('drop table if exists TBL')
            self.conn.commit()
            
            self._execute('alter table TBL2 rename to TBL')
            self.conn.commit()
        else:
            # Initialize another temporary table
            self._execute('drop table if exists TBL')
            self.conn.commit()
            
            query = []
            for n in nsubset:
                query.append('%s %s'%(_sha1(n), self._get_sqltype(n)))
            query = ', '.join(query)
            query =  'create temp table TBL\n  (' + query + ')'
            self._execute(query)

            # build filter query
            query = []
            for item in where:
                # process item as a string
                if isinstance(item, _strobj):
                    tokens = []
                    for word in item.split():
                        if word in self.keys():
                            tokens.append(_sha1(word))
                        else:
                            tokens.append(word)
                    query.append(' '.join(tokens))

                # process item as a tuple
                else:
                    try:
                        (k,op,value) = item
                    except:
                        raise Exception('could not upack tuple from where')
                    
                    if _isfloat(value):
                        query.append(' %s %s %s'%(_sha1(k), op, value))
                    elif isinstance(value,list):
                        if _isfloat(value[0]):
                            args = ', '.join(str(v) for v in value)
                        else:
                            args = ', '.join('"%s"'%v for v in value)
                        query.append(' %s %s (%s)'%(_sha1(k), op, args))
                    else:
                        query.append(' %s %s "%s"'%(_sha1(str(k)), op, value))
                    
            query = ' and '.join(query)
            nstr = ', '.join(_sha1(n) for n in nsubset)
            query = 'insert into TBL select %s from TBL2\n where '%nstr + query
            
            # run query
            self._execute(query)
            self.conn.commit()

            # delete TBL2
            self._execute('drop table if exists TBL2')
            self.conn.commit()

    def _get_sqlite3_tbl_info(self):
        """
        private method to get a list of tuples containing information
        relevant to the current sqlite3 table

           args:
              None

           returns:
              list of tuples:
        |        Each tuple cooresponds to a column.
        |        Tuples include the column name, data type, whether or not the
        |        column can be NULL, and the default value for the column.
        """
        self.conn.commit()
        self._execute('PRAGMA table_info(TBL)')
        return list(self.cur)
    
    def pivot(self, val, rows=None, cols=None, aggregate='avg',
              where=None, attach_rlabels=False, method='valid'):
        """
        produces a contingency table according to the arguments and keywords
        provided.

           args:
              val: the colname to place as the data in the table

           kwds:
              rows: list of colnames whos combinations will become rows
                    in the table if left blank their will be one row
                    
              cols: list of colnames whos combinations will become cols
                    in the table if left blank their will be one col
                    
              aggregate: function applied across data going into each cell
                  of the table <http://www.sqlite.org/lang_aggfunc.html>_
                  
              where: list of tuples or list of strings for filtering data
              
              method:
                 'valid': only returns rows or columns with valid entries.

                 'full': return full factorial combinations of the
                         conditions specified by rows and cols
                         
           returns:
              :class:`PyvtTbl` object
        """
        
        if rows == None:
            rows = []
            
        if cols == None:
            cols = []
            
        if where == None:
            where = []
            
        ##############################################################
        # pivot programmatic flow                                    #
        ##############################################################
        #  1.  Check to make sure the table can be pivoted with the  #
        #      specified parameters                                  #
        #  2.  Create a sqlite table with only the data in columns   #
        #      specified by val, rows, and cols. Also eliminate      #
        #      rows that meet the exclude conditions                 #
        #  3.  Build rnames and cnames lists                         #
        #  4.  Build query based on val, rows, and cols              #
        #  5.  Run query                                             #
        #  6.  Read data to from cursor into a list of lists         #
        #  7.  Query grand, row, and column totals                   #
        #  8.  Clean up                                              #
        #  9.  flatten if specified                                  #
        #  10. Initialize and return PyvtTbl Object                  #
        ##############################################################

        #  1. Check to make sure the table can be pivoted with the
        #     specified parameters
        ##############################################################
        #  This may seem excessive but it provides better feedback
        #  to the user if the errors can be parsed out before had
        #  instead of crashing on confusing looking code segments
            
                
        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')

        # check the supplied arguments
        if val not in self.keys():
            raise KeyError(val)

        if not hasattr(rows, '__iter__'):
            raise TypeError( "'%s' object is not iterable"
                             % type(cols).__name__)

        if not hasattr(cols, '__iter__'):
            raise TypeError( "'%s' object is not iterable"
                             % type(cols).__name__)
        
        for k in rows:
            if k not in self.keys():
                raise KeyError(k)
            
        for k in cols:
            if k not in self.keys():
                raise KeyError(k)

        # check for duplicate names
        dup = Counter([val] + rows + cols)
        del dup[None]
        if not all(count == 1 for count in dup.values()):
            raise Exception('duplicate labels specified')

        # check aggregate function
        aggregate = aggregate.lower()

        if aggregate not in self.aggregates:
            raise ValueError("supplied aggregate '%s' is not valid"%aggregate)
        
        # check to make sure where is properly formatted
        # todo
        
        #  2. Create a sqlite table with only the data in columns
        #     specified by val, rows, and cols. Also eliminate
        #     rows that meet the exclude conditions      
        ##############################################################
        self._build_sqlite3_tbl([val] + rows + cols, where)
        
        #  3. Build rnames and cnames lists
        ##############################################################
        
        # Refresh conditions list so we can build row and col list
        self._execute('select %s from TBL'
                      %', '.join(_sha1(n) for n in [val] + rows + cols))
        Zconditions = DictSet(zip([val]+rows+cols, zip(*list(self.cur))))

        # rnames_mask and cnanes_mask specify which unique combinations of
        # factor conditions have valid entries in the table.
        #   1 = valid
        #   0 = not_valid
        
        # Build rnames
        if rows == []:
            rnames = [1]
            rnames_mask = [1]
        else:
            rnames = []
            rnames_mask = []

            conditions_set = set(zip(*[self[n] for n in rows]))
            for vals in Zconditions.unique_combinations(rows):
                rnames_mask.append(tuple(vals) in conditions_set)                    
                rnames.append(zip(rows,vals))
        
        # Build cnames
        if cols == []:
            cnames = [1]
            cnames_mask = [1]
        else:
            cnames = []
            cnames_mask = []

            conditions_set = set(zip(*[self[n] for n in cols]))
            for vals in Zconditions.unique_combinations(cols):
                cnames_mask.append(tuple(vals) in conditions_set)
                cnames.append(zip(cols,vals))
        
        
        #  4. Build query based on val, rows, and cols
        ##############################################################
        #  Here we are using string formatting to build the query.
        #  This method is generally discouraged for security, but
        #  in this circumstance I think it should be okay. The column
        #  labels are protected with leading and trailing underscores.
        #  The rest of the query is set by the logic.
        #
        #  When we pass the data in we use the (?) tuple format
        if aggregate == 'tolist':
            agg = 'group_concat'
        else:
            agg = aggregate
            
        query = ['select ']            
        if rnames == [1] and cnames == [1]:
            query.append('%s( %s ) from TBL'%(agg, _sha1(val)))
        else:
            if rnames == [1]:
                query.append(_sha1(val))
            else:
                query.append(', '.join(_sha1(r) for r in rows))

            if cnames == [1]:
                query.append('\n  , %s( %s )'%(agg, _sha1(val)))
            else:
                for cs in cnames:
                    query.append('\n  , %s( case when '%agg)
                    if all(map(_isfloat, zip(*cols)[1])):
                        query.append(
                        ' and '.join(('%s=%s'%(_sha1(k), v) for k, v in cs)))
                    else:
                        query.append(
                        ' and '.join(('%s="%s"'%(_sha1(k) ,v) for k, v in cs)))
                    query.append(' then %s end )'%_sha1(val))

            if rnames == [1]:
                query.append('\nfrom TBL')
            else:                
                query.append('\nfrom TBL group by ')
                
                for i, r in enumerate(rows):
                    if i != 0:
                        query.append(', ')
                    query.append(_sha1(r))

        #  5. Run Query
        ##############################################################
        self._execute(''.join(query))

        #  6. Read data from cursor into a list of lists
        ##############################################################

        data, mask = [],[]
        val_type = self._get_sqltype(val)
        fill_val = self._get_mafillvalue(val)

        # keep the columns with the row labels
        if attach_rlabels:
            cnames = [(r, '') for r in rows].extend(cnames)
            cnames_mask = [1 for i in _xrange(len(rows))].extend(cnames_mask)

        if aggregate == 'tolist':
            if method=='full':
                i=0
                for row in self.cur:
                    while not rnames_mask[i]:
                        data.append([[fill_val] for j in _xrange(len(cnames))])
                        mask.append([[True] for j in _xrange(len(cnames))])
                        i+=1
                        
                    data.append([])
                    mask.append([])
                    for cell, _mask in zip(list(row)[-len(cnames):], cnames_mask):
                        if cell == None or not _mask:
                            data[-1].append([fill_val])
                            mask[-1].append([True])
                        else:
                            if val_type == 'real' or val_type == 'integer':
                                split =cell.split(',')
                                data[-1].append(map(float, split))
                                mask[-1].append([False for j in _xrange(len(split))])
                            else:
                                split =cell.split(',')
                                data[-1].append(split)
                                mask[-1].append([False for j in _xrange(len(split))])
                    i+=1
            else:
                for row in self.cur:
                    data.append([])
                    mask.append([])
                    for cell, _mask in zip(list(row)[-len(cnames):], cnames_mask):
                        if _mask:
                            if cell == None:
                                data[-1].append([fill_val])
                                mask[-1].append([True])
                            elif val_type == 'real' or val_type == 'integer':
                                split =cell.split(',')
                                data[-1].append(map(float, split))
                                mask[-1].append([False for j in _xrange(len(split))])
                            else:
                                split =cell.split(',')
                                data[-1].append(split)
                                mask[-1].append([False for j in _xrange(len(split))])

            # numpy arrays must have the same number of dimensions so we need to pad
            # cells to the maximum dimension of the data
            max_len = max(_flatten([[len(c) for c in L] for L in data]))

            for i,L in enumerate(data):
                for j,c in enumerate(L):
                    for k in _xrange(max_len - len(data[i][j])):
                        data[i][j].append(fill_val)
                        mask[i][j].append(True)
                        
        else:
            if method=='full':
                i=0
                for row in self.cur:
                    while not rnames_mask[i]:
                        data.append([fill_val for j in _xrange(len(cnames))])
                        mask.append([True for j in _xrange(len(cnames))])
                        i+=1

                    row_data = list(row)[-len(cnames):]
                    data.append([(fill_val,v)[m] for v,m in zip(row_data, cnames_mask)])
                    mask.append([not m for v,m in zip(row_data, cnames_mask)])
                    i+=1
            else:
                for row in self.cur:
                    row_data = list(row)[-len(cnames):]
                    data.append([v for v,m in zip(row_data, cnames_mask) if m])
                    mask.append([False for m in cnames_mask if m])

        #  7. Get totals
        ##############################################################
        row_tots, col_tots, grand_tot = [], [], np.nan
        row_mask, col_mask = [], []
        
        if aggregate not in ['tolist', 'group_concat', 'arbitrary']:
            query = 'select %s( %s ) from TBL'%(agg, _sha1(val))
            self._execute(query)
            grand_tot = list(self.cur)[0][0]

            if cnames != [1] and rnames != [1]:
                query = ['select %s( %s ) from TBL group by'%(agg, _sha1(val))]
                query.append(', '.join(_sha1(r) for r in rows))
                self._execute(' '.join(query))
                
                if method=='full':
                    i=0
                    row_tots=[]
                    row_mask=[]
                    for tup in self.cur:
                        while not rnames_mask[i]:
                            row_tots.append(fill_val)
                            row_mask.append(True)
                            i+=1
                            
                        row_tots.append(tup[0])
                        row_mask.append(False)
                        i+=1
                else:
                    row_tots = [tup[0] for tup in self.cur]    
                    row_mask = [False for z in row_tots]   
                
                query = ['select %s( %s ) from TBL group by'%(agg, _sha1(val))]
                query.append(', '.join(_sha1(r) for r in cols))
                self._execute(' '.join(query))

                if method=='full':
                    i=0
                    col_tots=[]
                    col_mask=[]
                    for tup in self.cur:
                        while not cnames_mask[i]:
                            col_tots.append(fill_val)
                            col_mask.append(True)
                            i+=1
                            
                        col_tots.append(tup[0])
                        col_mask.append(False)
                        i+=1
                else:
                    
                    col_tots = [tup[0] for tup in self.cur]    
                    col_mask = [False for z in col_tots]
                    
        row_tots = np.ma.array(row_tots, mask=row_mask)
        col_tots = np.ma.array(col_tots, mask=col_mask)
        
        #  8. Clean up
        ##############################################################
        self.conn.commit()

        #  9. Build rnames and cnames if method=='valid'
        ##############################################################
        if method=='valid':
            rnames = [n for n,m in zip(rnames,rnames_mask) if m]
            cnames = [n for n,m in zip(cnames,cnames_mask) if m]
        
        #  10. Initialize and return PyvtTbl Object
        ##############################################################
##
##        print(data)
##        print(mask)
##        print(rnames)
##        print(cnames)
##        print(col_tots)
##        print(row_tots)
##        print(grand_tot)
##        print()
##        
        return PyvtTbl(data, val, Zconditions, rnames, cnames, aggregate,
                       mask=mask, 
                       row_tots=row_tots, col_tots=col_tots, grand_tot=grand_tot,
                       attach_rlabels=attach_rlabels)
            
    def select_col(self, key, where=None):
        """
        determines rows in table that satisfy the conditions given by where and returns
        the values of key in the remaining rows

           args:
              key: column label of data to return

           kwds:
              where: constraints to apply to table before returning data

           returns:
               a list
               
           example:
              >>> ...
              >>> print(df)
              first      last       age   gender 
              ==================================
              Roger   Lew            28   male   
              Bosco   Robinson        5   male   
              Megan   Whittington    26   female 
              John    Smith          51   male   
              Jane    Doe            49   female 
              >>> df.select_col('age', where='gender == "male"')
              [28, 5, 51]
              >>> 
        """
        if where == None:
            where = []

        # 1.
        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')

        # 2.
        # check the supplied arguments
        if key not in self.keys():
            raise KeyError(val)

##        # check to make sure exclude is mappable
##        # todo
##
##        # warn if exclude is not a subset of self.conditions
##        if not set(self.keys()) >= set(tup[0] for tup in where):
##            warnings.warn("where is not a subset of table conditions",
##                          RuntimeWarning)
            
        if where == []: 
            return copy(self[key])             
        else:
            self._build_sqlite3_tbl([key], where)
            self._execute('select * from TBL')
            return [r[0] for r in self.cur]

    def sort(self, order=None):
        """
        sort the table in-place

           kwds:
              order: is a list of factors to sort by
              to reverse order append " desc" to the factor

           returns:
              None
              
           example:
              >>> from pyvttbl import DataFrame
              >>> from collections import namedtuple
              >>> Person = namedtuple('Person',['first','last','age','gender'])
              >>> df =DataFrame()
              >>> df.insert(Person('Roger', 'Lew', 28, 'male')._asdict())
              >>> df.insert(Person('Bosco', 'Robinson', 5, 'male')._asdict())
              >>> df.insert(Person('Megan', 'Whittington', 26, 'female')._asdict())
              >>> df.insert(Person('John', 'Smith', 51, 'male')._asdict())
              >>> df.insert(Person('Jane', 'Doe', 49, 'female')._asdict())
              >>> df.sort(['gender', 'age'])
              >>> print(df)
              first      last       age   gender 
              ==================================
              Megan   Whittington    26   female 
              Jane    Doe            49   female 
              Bosco   Robinson        5   male   
              Roger   Lew            28   male   
              John    Smith          51   male   
              >>> 
        """
        if order == None:
            order = []

        # Check arguments        
        if self == {}:
            raise Exception('Table must have data to sort data')
        
        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')
        
        if not hasattr(order, '__iter__'):
            raise TypeError( "'%s' object is not iterable"
                             % type(order).__name__)

        # check or build order
        if order == []:
            order = self.keys()

        # there are probably faster ways to do this, we definitely need
        # to treat the words as tokens to avoid problems were column
        # names are substrings of other column names
        for i, k in enumerate(order):
            ks = k.split()
            if ks[0] not in self.keys():
                raise KeyError(k)
            
            if len(ks) == 1:
                order[i] = _sha1(ks[0])

            elif len(ks) == 2:
                if ks[1].lower() not in ['desc', 'asc']:
                    raise Exception("'order arg must be 'DESC' or 'ASC'")
                order[i] = '%s %s'%(_sha1(ks[0]), ks[1])

            elif len(ks) > 2:
                raise Exception('too many parameters specified')

        # build table
        self._build_sqlite3_tbl(self.keys())

        # build and excute query
        query = 'select * from TBL order by ' + ', '.join(order)
        self._execute(query)

        # read sorted order from cursor
        d = []
        for row in self.cur:
            d.append(list(row))

        d = zip(*d) # transpose
        for i, n in enumerate(self.keys()):
            self[n] = list(d[i])

    def where(self, where):
        """
        Applies the where filter to a copy of the DataFrame, and
        returns the new DataFrame. The associated DataFrame is not copied.

           args:
              where: criterion to apply to new table

           returns:
              a new :class:`DataFrame`

           example:
              >>> ...
              >>> print(df)
              first      last       age   gender 
              ==================================
              Roger   Lew            28   male   
              Bosco   Robinson        5   male   
              Megan   Whittington    26   female 
              John    Smith          51   male   
              Jane    Doe            49   female
              >>> print(df.where('age > 20 and age < 45'))
              first      last       age   gender 
              ==================================
              Roger   Lew            28   male   
              Megan   Whittington    26   female 
              >>> 
        """
        new = DataFrame()
        
        self._build_sqlite3_tbl(self.keys(), where)
        self._execute('select * from TBL')
        for n, values in zip(self.keys(), zip(*list(self.cur))):
            new[n] = list(values)        

        return new
    
    def where_update(self, where):
        """
        Applies the where filter in-place.
        
           args:
              where: criterion to apply to table

           returns:
              None
        """
        self._build_sqlite3_tbl(self.keys(), where)
        self._execute('select * from TBL')
        for n, values in zip(self.keys(), zip(*list(self.cur))):
            del self[n]
            self[n] = list(values)
    
    def validate(self, criteria, verbose=False, report=False):
        """
        validate the data in the table.

           args:
              criteria: a dict whose keys should coorespond to columns in the table.
              The values should be functions which take a single parameter and return
              a boolean.

           kwds:
              verbose:
                 True: provide real-time feedback
                 
                 False: don't provide feedback (default)
              
              report:
                 True: print a report upon completion
                 
                 False: don't print report (default)

           returns:
              True: the criteria was satisfied
              
              False: the critera was not satisfied
           
            example:
              >>> ...
              >>> print(df)
              first      last       age   gender 
              ==================================
              Roger   Lew            28   male   
              Bosco   Robinson        5   male   
              Megan   Whittington    26   female 
              John    Smith          51   male   
              Jane    Doe            49   female
              >>> def isint(x):
                      try : return int(x)-float(x)==0
                      except:  return False
              >>> df.validate({'age' : lambda x: isint(x),
                               'gender' : lambda x: x in ['male', 'female']},
                               verbose=True, report=True)                    
              Validating gender:
              .....
              Validating age:
              .....
              Report:
                Values tested: 10 
                Values passed: 10 
                Values failed: 0
              ***Validation PASSED***
              True
              >>>
              
        """
        # do some checking
        if self == {}:
            raise Exception('table must have data to validate data')
        
        try:        
            c = set(criteria.keys())
            s = set(self.keys())
        except:
            raise TypeError('criteria must be mappable type')

        # check if the criteria dict has keys that aren't in self
        all_keys_found = bool((c ^ (c & s)) == set())

        # if the user doesn't want a detailed report we don't have
        # to do as much book keeping and can greatly simplify the
        # logic
        if not verbose and not report:
            if all_keys_found:
                return all(all(map(criteria[k], self[k])) for k in criteria)
            else:
                return False

        # loop through specified columns and apply the
        # validation function to each value in the column
        valCounter = Counter()
        reportDict = {}
        for k in (c & s):
            reportDict[k] = []
            if verbose:
                print('\nValidating %s:'%k)
                
            for i,v in enumerate(self[k]):
                try:
                    func = criteria[k]
                    result = func(v)
                except:
                    result = False
                    valCounter['code_failures'] +=1
                
                valCounter[result] += 1
                valCounter['n'] += 1

                if result:
                    if verbose:
                        print('.', end='')
                else:
                    reportDict[k].append(
                        "Error: on index %i value "
                        "'%s' failed validation"%(i, str(v)))
                    if verbose:
                        print('X', end='')
            if verbose:
                print()

        # do some book keeping
        pass_or_fail = (valCounter['n'] == valCounter[True]) & all_keys_found

        # print a report if the user has requested one
        if report:
            print('\nReport:')
            for k in (c&s):
                if len(reportDict[k]) > 0:
                    print('While validating %s:'%k)
                for line in reportDict[k]:
                    print('   ',line)

            print(  '  Values tested:', valCounter['n'],
                  '\n  Values passed:', valCounter[True],
                  '\n  Values failed:', valCounter[False])

            if valCounter['code_failures'] != 0:
                print('\n  (%i values failed because '
                      'func(x) did not properly execute)'
                      %valCounter['code_failures'])

            if not all_keys_found:
                print('\n  Error: criteria dict contained '
                      'keys not found in table:'
                      '\n   ', ', '.join(c ^ (c & s)))

            if pass_or_fail:
                print('\n***Validation PASSED***')
            else:
                print('\n***Validation FAILED***')

        # return the test result
        return pass_or_fail

    def attach(self, other):
        """
        attaches a second :class:`DataFrame` to self

           args:
              other: a :class:`DataFrame` object whose key set matches self

           return:
              None
        """

        # do some checking
        if not isinstance(other, DataFrame):
            raise TypeError('second argument must be a DataFrame')
        
        if not self._are_col_lengths_equal():
            raise Exception('columns in self have unequal lengths')
        
        if not other._are_col_lengths_equal():
            raise Exception('columns in other have unequal lengths')

        if not set(self.keys()) == set(other.keys()):
            raise Exception('self and other must have the same columns')

        if not all(self._get_sqltype(n) == other._get_sqltype(n) for n in self):
            raise Exception('types of self and other must match')

        # perform attachment
        for n in self.keys():
            self[n] = np.concatenate((self[n], other[n]))

        # update state variables
        self.conditions = DictSet([(n, list(self[n])) for n in self])

    def insert(self, row):
        """
        insert a row into the table

           args:
              row: should be mappable. e.g. a dict or a list with key/value pairs.

           returns:
              None

           example:
              >>> from pyvttbl import DataFrame
              >>> from collections import namedtuple
              >>> Person = namedtuple('Person',['first','last','age','gender'])
              >>> df =DataFrame()
              >>> df.insert(Person('Roger', 'Lew', 28, 'male')._asdict())
              >>> df.insert(Person('Bosco', 'Robinson', 5, 'male')._asdict())
              >>> df.insert(Person('Megan', 'Whittington', 26, 'female')._asdict())
              >>> print(df)
              first      last       age   gender 
              ==================================
              Roger   Lew            28   male   
              Bosco   Robinson        5   male   
              Megan   Whittington    26   female 
              >>> 
        """
        try:
            c = set(dict(row).keys())
            s = set(self.keys())
        except:
            raise TypeError('row must be mappable type')
        
        # the easy case
        if self == {}:
            # if the table is empty try and unpack the table as
            # a row so it preserves the order of the column names
            if isinstance(row, list):
                for (k, v) in row:
                    self[k] = [v]
                    self.conditions[k] = [v]
            else:
                for (k, v) in row.items():
                    self[k] = [v]
                    self.conditions[k] = [v]
        elif c - s == set():
            for (k, v) in OrderedDict(row).items():
                self[k]=np.concatenate((self[k],
                                        np.array([v], dtype=self._get_nptype(k))))
                self.conditions[k].add(v)
        else:
            raise Exception('row must have the same keys as the table')

    def write(self, where=None, fname=None, delimiter=','):
        """
        write the contents of the DataFrame to a plaintext file

           kwds:
              where: criterion to apply to table before writing to file
              
              fname: the path + name of the output file

              delimiter: string to separate row cells (default = ",")
        """
        if where == None:
            where = []

        if self == {}:
            raise Exception('Table must have data to print data')

        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')

        if self.shape()[1] < 1:
            raise Exception('Table must have at least one row to print data')
        
        # check or build fname
        if fname != None:
            if not isinstance(fname, _strobj):
                raise TypeError('fname must be a string')
        else:
            lnames = [str(n).lower().replace('1','') for n in self.keys()]
            fname = 'X'.join(lnames)

            if delimiter == ',':
                fname += '.csv' 
            elif delimiter == '\t':               
                fname += '.tsv'
            else:
                fname += '.txt'

        with open(fname,'wb') as fid:
            wtr = csv.writer(fid, delimiter=delimiter)
            wtr.writerow(self.keys())

            if where == []: 
                wtr.writerows(zip(*list(self[n] for n in self)))
            else:
                self._build_sqlite3_tbl(self.keys(), where)
                self._execute('select * from TBL')
                wtr.writerows(list(self.cur))

    def descriptives(self, key, where=None):
        """
        Conducts a descriptive statistical analysis of the data in self[key].

           args:
              key: column label

           kwds:
              where: criterion to apply to table before running analysis

           returns:
              a :mod:`pyvttbl.stats`. :class:`Descriptives` object
        """

        if where == None:
            where = []

        if self == {}:
            raise Exception('Table must have data to calculate descriptives')

        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')

        if key not in self.keys():
            raise KeyError(key)
        
        V = self.select_col(key, where=where)
        d = stats.Descriptives()
        d.run(V, key)
        return d

    def summary(self, where=None):
        """
        prints the descriptive information for each column in DataFrame

           kwds:
              where: criterion to apply to table before running analysis

           returns:
              None
        """

        for (cname,dtype) in self.keys():
            if dtype in ['real', 'integer']:
                print(self.descriptives(cname, where))
                print()

            else:
                print('%s contains non-numerical data\n'%cname)

    def marginals(self, key, factors, where=None):
        if where == None:
            where = []

        if self == {}:
            raise Exception('Table must have data to find marginals')

        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')
        
        m = stats.Marginals()
        m.run(self, key, factors, where)
        return m


    marginals.__doc__ = stats.Marginals.__doc__
    
    def anova1way(self, val, factor, posthoc='tukey', where=None):
        """
        Conducts a one-way analysis of variance
        on val over the conditions in factor. The conditions do not necessarily
        need to have equal numbers of samples.

           args:
              val: dependent variable

              factor: a dummy coded column label

            kwds:
               posthoc:
                  'tukey': conduct Tukey posthoc tests
                  
                  'SNK': conduct Newman-Keuls posthoc tests

            where:
               conditions to apply before running analysis

           return:
              an :class:`pyvttbl.stats.Anova1way` object 
        """
        if where == None:
            where = []

        if self == {}:
            raise Exception('Table must have data to find marginals')

        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')

        # build list of lists for ANOVA1way object
        list_of_lists = []
        pt = self.pivot(val,rows=[factor],
                        aggregate='tolist',
                        where=where)
        for L in pt:
            list_of_lists.append(L.flatten().tolist())
        
        # build list of condiitons
        conditions_list = [tup[1] for [tup] in pt.rnames]

        a = stats.Anova1way()
        a.run(list_of_lists, val, factor, conditions_list, posthoc=posthoc)
        return a
    
    def chisquare1way(self, observed, expected_dict=None,
                      alpha=0.05, where=None):
        """
        conducts a one-way chi-square goodness-of-fit test on the data in observed

           args:
              observed: column label containing categorical observations
              
           kwds:
               expected_dict: a dictionary object with keys matching the categories
                              in observed and values with the expected counts. The
                              categories in the observed column must be a subset of
                              the keys in the expected_dict. If expected_dict is None,
                              the total N is assumed to be equally distributed across
                              all groups.

               alpha: the type-I error probability
               
               where:
                  conditions to apply before running analysis

           return:
              an :class:`pyvttbl.stats.ChiSquare1way` object 
        """

        # ched the expected_dict
        if expected_dict != None:
            try:
                expected_dict2 = dict(copy(expected_dict))
            except:
                raise TypeError("'%s' is not a mappable type"
                                %type(expected_dict).__name__())

            if not self.conditions[observed] <= set(expected_dict2.keys()):
                raise Exception('expected_dict must contain a superset of  '
                                'of the observed categories')
        else:
            expected_dict2 = Counter()

        # find the counts
        observed_dict=Counter(self.select_col(observed, where))

        # build arguments for ChiSquare1way
        observed_list = []
        expected_list = []
        conditions_list = sorted(set(observed_dict.keys()) |
                                 set(expected_dict2.keys()))
        for key in conditions_list:
            observed_list.append(observed_dict[key])
            expected_list.append(expected_dict2[key])

        if expected_dict == None:
            expected_list = None

        # run analysis
        x = stats.ChiSquare1way()
        x.run(observed_list, expected_list, conditions_list=conditions_list,
              measure=observed, alpha=alpha)

        return x

    def chisquare2way(self, rfactor, cfactor, alpha=0.05, where=None):
        """
        conducts a two-way chi-square goodness-of-fit test on the data in observed

           args:
              rfactor: column key
              
              cfactor: column key
              
           kwds:
               alpha: the type-I error probability 

               where:
                  conditions to apply before running analysis

           return:
              an :class:`pyvttbl.stats.ChiSquare2way` object 
        """
        row_factor = self.select_col(rfactor, where)
        col_factor = self.select_col(cfactor, where)

        x2= stats.ChiSquare2way()
        x2.run(row_factor, col_factor, alpha=alpha)
        return x2


    def correlation(self, variables, coefficient='pearson',
                    alpha=0.05, where=None):
        """
        produces a correlation matrix and conducts step-down significance testing
        on the column labels in variables.

           args:
              variables: column keys to include in correlation matrix
              
           kwds:
               coefficient:
                  { 'pearson', 'spearman', 'kendalltau', 'pointbiserial' }
                  
               alpha: the type-I error probability 

               where:
                  conditions to apply before running analysis

           return:
              an :class:`pyvttbl.stats.Correlation` object 
        """
        
        list_of_lists = []
        for var in sorted(variables):
            list_of_lists.append(list(self.select_col(var, where)))

        cor= stats.Correlation()
        cor.run(list_of_lists, sorted(variables),
                coefficient=coefficient, alpha=alpha)
        return cor
                
    def ttest(self, aname, bname=None, pop_mean=0., paired=False,
              equal_variance=True, where=None):
        """
        produces a correlation matrix and conducts step-down significance testing
        on the column labels in variables.

           args:
              aname: column key
              
           kwds:
               bname: is not specified a one-sample t-test is performed on
                    comparing the values in column aname with a hypothesized
                    population mean.
                    
               pop_mean: specifies the null population mean for one-sample t-test.
                    Ignored if bname is supplied

               paired:
                  True: a paired t-test is conducted
                  
                  False: an independent samples t-test is conducted
                  
               equal_variance:
                  True: assumes aname and bname have equal variance
                  
                  False: assumes aname and bname have unequal variance

               where:
                  conditions to apply before running analysis

           return:
              an :class:`pyvttbl.stats.Ttest` object 
        """
        


        if where == None:
            where = []

        if self == {}:
            raise Exception('Table must have data to find marginals')

        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')
        
        adata = self.select_col(aname, where=where)
        if bname != None:
            bdata = self.select_col(bname, where=where)
        else:
            bdata = None
        
        t = stats.Ttest()
        t.run(adata, bdata, pop_mean=pop_mean,
              paired=paired, equal_variance=equal_variance,
              aname=aname, bname=bname)
        return t
        
    def histogram(self, key, where=None, bins=10,
                  range=None, density=False, cumulative=False):

        """
        Conducts a histogram analysis of the data in self[key].

           args:
              key: column label of dependent variable

           kwds:
              where: criterion to apply to table before running analysis

              bins: number of bins (default = 10)

              range: list of length 2 defining min and max bin edges

           returns:
              a :mod:`pyvttbl.stats`. :class:`Descriptives` object
        """
        if where == None:
            where = []
            
        if self == {}:
            raise Exception('Table must have data to calculate histogram')

        # check to see if data columns have equal lengths
        if not self._are_col_lengths_equal():
            raise Exception('columns have unequal lengths')

        if key not in self.keys():
            raise KeyError(key)
        
        V = sorted(self.select_col(key, where=where))
        h = stats.Histogram()
        h.run(V, cname=key, bins=bins, range=range,
              density=density, cumulative=cumulative)
        
        return h

    def anova(self, dv, sub='SUBJECT', wfactors=None, bfactors=None,
              measure='', transform='', alpha=0.05):
        """
        conducts a betweeen, within, or mixed, analysis of variance

           args:
              dv: label containing dependent variable
         

           kwds:
              wfactors: list of within variable factor labels

              bfactors: list of between variable factor labels

              sub: label coding subjects (or the isomorphism)

              measure: string to describe dv (outputs '<dv> of
                     <measure>') intended when dv name is generic
                     (e.g., MEAN, RMS, SD, ...)
                     
              transform: string specifying a data transformation

                 =======================  ===============  ==================  
                 STRING OPTION            TRANSFORM        COMMENTS
                 =======================  ===============  ==================
                 ''                       X                default
                 'log','log10'            numpy.log(X)     base 10 transform
                 'reciprocal', 'inverse'  1/X
                 'square-root', 'sqrt'    numpy.sqrt(X)
                 'arcsine', 'arcsin'      numpy.arcsin(X)
                 'windsor 10'             windsor(X, 10)   10% windosr trim
                 =======================  ===============  ==================
        """
        aov=stats.Anova()
        aov.run(self, dv, sub=sub, wfactors=wfactors, bfactors=bfactors,
                measure=measure, transform=transform, alpha=alpha)
        return aov
        
    def histogram_plot(self, val, **kwargs):
        return plotting.histogram_plot(self, val, **kwargs)

    histogram_plot.__doc__ = plotting.histogram_plot.__doc__
    
    def scatter_plot(self, aname, bname, **kwargs):
        return plotting.scatter_plot(self, aname, bname, **kwargs)

    scatter_plot.__doc__ = plotting.scatter_plot.__doc__

    def box_plot(self, val, factors=None, **kwargs):
        return plotting.box_plot(self, val, factors=factors, **kwargs)

    box_plot.__doc__ = plotting.box_plot.__doc__

    def interaction_plot(self, val, xaxis, **kwargs):
        return plotting.interaction_plot(self, val, xaxis, **kwargs)

    interaction_plot.__doc__ = plotting.interaction_plot.__doc__
    
    def scatter_matrix(self, variables, **kwargs):
        return plotting.scatter_matrix(self, variables, **kwargs)

    scatter_matrix.__doc__ = plotting.scatter_matrix.__doc__        

class _ptmathmethod(object):
    """
    Defines a wrapper for arithmetic array methods (add, mul...).
    """
    def __init__ (self, methodname):
        self.__name__ = methodname
        self.__doc__ = getattr(np.ma.MaskedArray, methodname).__doc__
        self.obj = None

    def __get__(self, obj, objtype=None):
        "Gets the calling object."
        self.obj = obj
        return self

    def __call__ (self, other, *args):
        "Execute the call behavior."
        
        instance = self.obj

        func = getattr(super(PyvtTbl, instance), self.__name__)
        data = np.ma.MaskedArray(func(other, *args), subok=False)

        if isinstance(other, PyvtTbl):
            func = getattr(instance.row_tots, self.__name__)
            row_tots = func(other.row_tots, *args)

            func = getattr(instance.col_tots, self.__name__)
            col_tots = func(other.col_tots, *args)

            func = getattr(np.ma.array([instance.grand_tot]), self.__name__)
            grand_tot = func(other.grand_tot, *args)[0]
            
        elif _isfloat(other):        
            func = getattr(instance.row_tots, self.__name__)
            row_tots = func(other, *args)

            func = getattr(instance.col_tots, self.__name__)
            col_tots = func(other, *args)

            func = getattr(np.ma.array([instance.grand_tot]), self.__name__)
            grand_tot = func(other, *args)[0]

        else:
            row_tots = np.ma.masked_equal(np.zeros(len(instance.row_tots)), 0.)
            col_tots = np.ma.masked_equal(np.zeros(len(instance.col_tots)), 0.)
            grand_tot = np.ma.masked
            
        return PyvtTbl(data,
                       val=instance.val,
                       conditions=instance.conditions,
                       rnames=instance.rnames,
                       cnames=instance.cnames,
                       aggregate='N/A',
                       row_tots=row_tots,
                       col_tots=col_tots,
                       grand_tot=grand_tot,
                       attach_rlabels=instance.attach_rlabels)
            
    
class PyvtTbl(np.ma.MaskedArray, object):
    """
    container holding the pivoted data
    """

    def __new__(cls, data, val, conditions, rnames, cnames, aggregate, **kwds):
        """
        creates a new PyvtTbl from scratch

           args:
              data: np.ma.array object holding pivoted data

              val: string label for the data in the table

              conditions: Dictset representing the factors and levels in the table

              rnames: list of row labels

              cnames: list of column labels

              aggregate: string describing the aggregate function applied to the data

           kwds:
              calc tots: bool specifying whether totals were calculated

              row_tots: row totals in a MaskedArray

              col_tots: column totals in a MaskedArray

              grand_tot: float holding grand total

              attach_rlabels: bool specifying whether row labels are part of the table

        |   subclassing Numpy objects are a little different from subclassing other objects.
        |   see: http://docs.scipy.org/doc/numpy/user/basics.subclassing.html
        """
        if data == None:
            data = []

        maparms = dict(copy=kwds.get('copy',False),
                       dtype=kwds.get('dtype',None),
                       fill_value=kwds.get('fill_value',None),
                       subok=kwds.get('subok',True),
                       keep_mask=kwds.get('keep_mask',True),
                       hard_mask=kwds.get('hard_mask',False))

        mask = kwds.get('mask', np.ma.nomask)
        obj = np.ma.MaskedArray.__new__(cls, data, mask=mask, ndmin=2, **maparms)

        # Get data
        if not kwds.get('subok',True) or not isinstance(obj, PyvtTbl):
            obj = obj.view(cls)

        # add attributes to instance
        obj.val = val
        obj.conditions = conditions
        obj.rnames = rnames
        obj.cnames = cnames
        obj.aggregate = aggregate

        if 'row_tots' in kwds:
            obj.row_tots = np.ma.array(kwds['row_tots'])
        else:
            obj.row_tots = []#np.ma.masked_equal(np.zeros(len(cnames)), 0.)

        if 'col_tots' in kwds:
            obj.col_tots = np.ma.array(kwds['col_tots'])
        else:
            obj.col_tots = []#np.ma.masked_equal(np.zeros(len(rnames)), 0.)
            
        obj.grand_tot = kwds.get('grand_tot', np.ma.masked)
        obj.where = kwds.get('where', [])
        obj.attach_rlabels = kwds.get('attach_rlabels', False)

        obj.subok = maparms['subok']
        obj.keep_mask = maparms['keep_mask']
        obj.hard_mask = maparms['hard_mask']
            
        return obj

    def __array_finalize__(self, obj):
        
        self.val = getattr(obj, 'val', None)
        self.conditions = getattr(obj, 'conditions', DictSet())
        self.rnames = getattr(obj, 'rnames', [1])
        self.cnames = getattr(obj, 'cnames', [1])
        self.aggregate = getattr(obj, 'aggregate', 'avg')

        if hasattr(obj, 'row_tots'):
            self.row_tots = np.ma.array(obj.row_tots)
        else:
            self.row_tots = np.ma.masked_equal(np.zeros(len(self.cnames)), 0.)
        
        if hasattr(obj, 'col_tots'):
            self.col_tots = np.ma.array(obj.col_tots)
        else:
            self.col_tots = np.ma.masked_equal(np.zeros(len(self.rnames)), 0.)
            
        self.grand_tot = getattr(obj, 'grand_tot', np.ma.masked)
        self.where = getattr(obj, 'where', [])
        self.attach_rlabels = getattr(obj, 'attach_rlabels', False)

        self.subok = getattr(obj, 'subok', True)
        self.keep_mask = getattr(obj, 'keep_mask', True)
        self.hard_mask = getattr(obj, 'hard_mask', False)

        np.ma.MaskedArray.__array_finalize__(self, obj)

    __array_finalize__.__doc__ = np.ma.MaskedArray.__array_finalize__.__doc__

    def transpose(self):
        """
        returns a transposed PyvtTbl object
        """
        return PyvtTbl(super(PyvtTbl,self).transpose(),
                             self.val,
                             self.conditions,
                             self.cnames,
                             self.rnames,
                             self.aggregate,
                             row_tots=self.col_tots,
                             col_tots=self.row_tots,
                             grand_tot=self.grand_tot,
                             attach_rlabels=self.attach_rlabels,
                             subok=self.subok,
                             keep_mask=self.keep_mask,
                             hard_mask=self.hard_mask)

    def astype(self, dtype):
        """
        Convert the input to an array.

           args:
              a: array_like Input data, in any form that can be converted to an array.  This
                 includes lists, lists of tuples, tuples, tuples of tuples, tuples
                 of lists and ndarrays.
           kwds:
              dtype: data-type. By default, the data-type is inferred from the input data.
              
              order: {'C', 'F'}  Whether to use row-major ('C') or column-major ('F' for FORTRAN)
                     memory representation.  Defaults to 'C'.

           returns:
              out: ndarray
                   Array interpretation of `a`.  No copy is performed if the input
                   is already an ndarray.  If `a` is a subclass of ndarray, a base
                   class ndarray is returned.
        """
        
        if hasattr(self.mask, '__iter__'):
            data = eval('np.ma.array(%s, mask=%s, dtype=dtype)'%\
                        (repr(self.tolist()), repr(self.mask.tolist())))
        else:
            data =eval('np.ma.array(%s, mask=%s, dtype=dtype)'%\
                        (repr(self.tolist()), repr(self.mask)))

        return PyvtTbl(data,
                      self.val,
                      self.conditions,
                      self.rnames,
                      self.cnames,
                      self.aggregate,
                      row_tots=self.row_tots.astype(dtype),
                      col_tots=self.col_tots.astype(dtype),
                      grand_tot=(dtype(self.grand_tot), np.ma.masked)\
                                [self.grand_tot is np.ma.masked],
                      attach_rlabels=self.attach_rlabels,
                      subok=self.subok,
                      keep_mask=self.keep_mask,
                      hard_mask=self.hard_mask)

    ######################################################################
    
    # Adapted from numpy.ma.core 
    
    def _get_flat(self):
        "Return a flat iterator."
        return np.ma.core.MaskedIterator(self)
    
    def _set_flat (self, value):
        "Set a flattened version of self to value."
        y = self.ravel()
        y[:] = value

    flat__doc__ = """\
    Flat iterator object to iterate over PyvtTbl.
    
    |   A `MaskedIterator` iterator is returned by ``x.flat`` for any PyvtTbl
        `x`. It allows iterating over the array as if it were a 1-D array,
        either in a for-loop or by calling its `next` method.
    
    |   Iteration is done in C-contiguous style, with the last index varying the
        fastest. The iterator can also be indexed using basic slicing or
        advanced indexing.
    """
    
    flat = property(fget=_get_flat, fset=_set_flat, doc=flat__doc__)

    ######################################################################

    def flatten(self):
        """
        returns a the PyvtTbl flattened as a MaskedArray
        """

        # probably a better way to do this if you really know what your doing.
        # subclassing numpy objects is not for the faint of heart
        
        obj = super(PyvtTbl,self).flatten()
        if hasattr(obj.mask, '__iter__'):
            return eval('np.ma.array(%s, mask=%s)'%\
                        (repr(obj.tolist()), repr(obj.mask.tolist())))
        else:
            return eval('np.ma.array(%s, mask=%s)'%\
                        (repr(obj.tolist()), repr(obj.mask)))

    # this is so Sphinx can find it
    def __iter__(self):
        return super(PyvtTbl, self).__iter__()
    
    __iter__.__doc__ = np.ma.MaskedArray.__iter__.__doc__

    def ndenumerate(self):
        """
        Multidimensional index iterator.
        
        returns:
           returns an iterator yielding pairs of array coordinates and values.

    """
        for i in _xrange(self.shape[0]):
            for j in _xrange(self.shape[1]):
                yield (i,j), self[i,j]


    def _get_rows(self):
        """
        returns a list of tuples containing row labels and conditions
        """
        if self.rnames == [1]:
            return [1]
        else:
            return [str(k) for (k, v) in self.rnames[0]]
        
    def _get_cols(self):
        """
        returns a list of tuples containing column labels and conditions
        """
        if self.cnames == [1]:
            return [1]
        else:
            return [str(k) for (k, v) in self.cnames[0]]

    def to_dataframe(self):
        """
        returns a DataFrame excluding row and column totals
        """
        if self == []:
            return DataFrame()

        
        rows = self._get_rows()
        cols = self._get_cols()

        # initialize DataFrame
        df = DataFrame()
        
        # no rows or cols were specified
        if self.rnames == [1] and self.cnames == [1]:
            # build the header
            header = ['Value']
            
        elif self.rnames == [1]: # no rows were specified
            # build the header
            header = [',\n'.join('%s=%s'%(f, c) for (f, c) in L) \
                      for L in self.cnames]
            
            if self.ndim == 2:
                rdata = self[0,:].flatten().tolist()
            else:
                rdata = [self[0,j].flatten().tolist()
                         for j in _xrange(len(self.cnames))]
                
            df.insert(zip(header, rdata))
                
        elif self.cnames == [1]: # no cols were specified
            # build the header
            header = rows + ['Value']

            for i, L in enumerate(self.rnames):
                if isinstance(self[i,0], PyvtTbl):
                    rdata = [c for (f, c) in L] + [self[i,0].flatten().tolist()]
                else:
                    rdata = [c for (f, c) in L] + [self[i,0]]
                    
                df.insert(zip(header, rdata))
                
        else: # table has rows and cols
            # build the header
            header = copy(rows)
            for L in self.cnames:
                header.append(',\n'.join('%s=%s'%(f, c) for (f, c) in L))
            
            for i, L in enumerate(self.rnames):
                
                if self.ndim == 2:
                    rdata =[c for (f, c) in L] + self[i,:].flatten().tolist()
                else:
                    rdata = [self[i,j].flatten().tolist()
                             for j in _xrange(len(self.cnames))]
                    
                df.insert(zip(header, rdata))

        return df

    def __getitem__(self, indx):
        """
        Return the item described by indx, as a PyvtTbl

           args:
              indx: index to array
                    can be int, tuple(int, int), tuple(slice, int),
                    tuple(int, slice) or tuple(slice, slice)

                    x[int] <==> x[int,:]

           returns:
              PyvtTbl that is at least 2-dimensional
              (unless indx is tuple(int, int))

        |   x.__getitem__(indx) <==> x[indx]
        """

        # x[i] <==> x[i,:] <==> x[i, slice(None, None, None)]
        if _isint(indx) or isinstance(indx, slice):
            return self.__getitem__((indx,slice(None, None, None)))
        
        obj = super(PyvtTbl, self).__getitem__(indx)

        if isinstance(obj, PyvtTbl):
            
            if self.rnames == [1] or _isint(indx[0]):
                m = 1
            else:
                m = len(self.rnames[indx[0]])

            if self.cnames == [1] or _isint(indx[1]):
                n = 1
            else:
                n = len(self.cnames[indx[1]])

##            print(self.ndim, self.shape)
##            print(obj.ndim, obj.shape)
##            print((m,n))
##            print()
##            
            if np.prod(obj.shape) == m*n:
                obj = np.reshape(obj, (m,n))

            else:
                obj = np.reshape(obj, (m,n,-1))
        
##            if obj.ndim == 1 and self.ndim == 2:
##                obj = np.reshape(obj, (m,n))
##
##            if obj.ndim == 1 and self.ndim == 3:
##                obj = np.reshape(obj, (m,n,-1))
##                
            obj.rnames = self.rnames[indx[0]]
            obj.cnames = self.cnames[indx[1]]

            if _isint(indx[0]): obj.rnames = [obj.rnames]
            if _isint(indx[1]): obj.cnames = [obj.cnames]
            
            obj.row_tots = np.ma.masked_equal(np.zeros(m), 0.)
            obj.col_tots = np.ma.masked_equal(np.zeros(n), 0.)

            obj.val = self.val

        return obj

    def __str__(self):
        """
        returns a human friendly string representation of the table
        """
##        return 'PyvtTbl:\n'+'\n\n'.join(
##            [super(PyvtTbl, self).__str__(),
##             'row_tots:'+str(self.row_tots),
##             'col_tots:'+str(self.col_tots)])+'\n\n'
    
        if self == []:
            return '(table is empty)'

        show_col_tots = any(np.invert(self.col_tots.mask))
        show_row_tots = any(np.invert(self.col_tots.mask))
        show_grand_tot = _isfloat(self.grand_tot) and not math.isnan(self.grand_tot)
        
        rows = self._get_rows()
        cols = self._get_cols()

        # initialize table
        tt = TextTable(max_width=0)

        # no rows or cols were specified
        if self.rnames == [1] and self.cnames == [1]:
            # build the header
            header = ['Value']

            # initialize the texttable and add stuff
            tt.set_cols_dtype(['t'])
            tt.set_cols_dtype(['l'])
            tt.add_row(self)
            
        elif self.rnames == [1]: # no rows were specified
            
            # build the header
            header = [',\n'.join('%s=%s'%(f, c) for (f, c) in L) \
                      for L in self.cnames]
            if show_grand_tot:
                header.append('Total')
            
            # initialize the texttable and add stuff
            # False and True evaluate as 0 and 1 for integer addition
            # and list indexing
            tt.set_cols_dtype(['a'] * (len(self.cnames)+show_grand_tot))
            tt.set_cols_align(['r'] * (len(self.cnames)+show_grand_tot))

            if self.ndim == 2:
                tt.add_row(self[0,:].flatten().tolist()+
                           ([],[self.grand_tot])[show_grand_tot])
            else:
                rdata = [self[0,j].flatten().tolist()
                         for j in _xrange(len(self.cnames))]
                
                tt.add_row(rdata + ([],[self.grand_tot])[show_grand_tot])
                        
        elif self.cnames == [1]: # no cols were specified
            
            # build the header
            header = rows + ['Value']
            
            # initialize the texttable and add stuff
            tt.set_cols_dtype(['t'] * len(rows) + ['a'])
            tt.set_cols_align(['l'] * len(rows) + ['r'])
            for i, L in enumerate(self.rnames):
                if isinstance(self[i,0], PyvtTbl):
                    tt.add_row([c for (f, c) in L] + [self[i,0].flatten().tolist()])
                else:
                    tt.add_row([c for (f, c) in L] + [self[i,0]])

            if show_grand_tot:
                tt.footer(['Total'] + 
                          ['']*(len(rows)-1) +
                          [self.grand_tot])

        else: # table has rows and cols
            # build the header
            header = copy(rows)
            for L in self.cnames:
                header.append(',\n'.join('%s=%s'%(f, c) for (f, c) in L))
            if show_row_tots:
                header.append('Total')

            dtypes = ['t'] * len(rows) + ['a'] * (len(self.cnames)+show_row_tots)
            aligns = ['l'] * len(rows) + ['r'] * (len(self.cnames)+show_row_tots)
            numcols = len(dtypes)

            # initialize the texttable and add stuff
            tt.set_cols_dtype(dtypes)
            tt.set_cols_align(aligns)
            if show_col_tots:
                for i, L in enumerate(self.rnames):
                    
                    tt.add_row([c for (f, c) in L] +
                               self[i,:].flatten().tolist() +
                               [self.row_tots[i]])

                tt.footer(['Total'] + 
                          ['']*(len(rows)-1) +
                          self.col_tots.tolist() +
                          [self.grand_tot])
                
            else:
                for i, L in enumerate(self.rnames):
                    if self.ndim == 2:
                        tt.add_row([c for (f, c) in L] +
                                   self[i,:].flatten().tolist())
                    else:
                        rdata = [self[i,j].flatten().tolist()
                                 for j in _xrange(len(self.cnames))]
                        
                        tt.add_row([c for (f, c) in L] + rdata)

        # add header and decoration
        tt.header(header)
        tt.set_deco(TextTable.HEADER | TextTable.FOOTER)

        # return the formatted table
        return '%s(%s)\n%s'%(self.aggregate, self.val, tt.draw())

    def __repr__(self):
        """
        returns a machine friendly string representation of the object
        """
        if self == []:
            return 'PyvtTbl()'

        args = repr(self.tolist())
        args += ", '%s'"%self.val
        args += ", %s"%repr(self.conditions)
        args += ", %s"%repr(self.rnames)
        args += ", %s"%repr(self.cnames)
        args += ", '%s'"%self.aggregate
        
        kwds = []

        if self.row_tots != None:
            # sometimes np.ma.array.mask is a bool, somtimes it is a list.
            # if we just copy the mask over it will first create a list and then
            # keep appending to the list everytime the object is reprized. Not sure if
            # if this is a bug or intentional. Anyways handling the masked string this
            # way makes it so repr(eval(repr(myPyvttbl))) = repr(myPyvttbl)
            
            mask_str =''
            if any(_flatten([self.row_tots.mask])):
                mask_str = ', mask=%s'%repr(self.row_tots.mask)
            kwds.append(', row_tots=np.ma.array(%s%s)'%\
                        (self.row_tots.tolist(), mask_str))
                
        if self.col_tots != None:
            mask_str =''
            if any(_flatten([self.col_tots.mask])):
                mask_str = ', mask=%s'%repr(self.col_tots.mask)
            kwds.append(', col_tots=np.ma.array(%s%s)'%\
                        (self.col_tots.tolist(), mask_str))
            
        if self.grand_tot != None:
            kwds.append(', grand_tot=%s'%repr(self.grand_tot))            
            
        if self.where != []:
            if isinstance(self.where, _strobj):
                kwds.append(", where='%s'"%self.where)
            else:
                kwds.append(", where=%s"%self.where)

        if self.attach_rlabels != False:
            kwds.append(', attach_rlabels=%s'%self.attach_rlabels)

        # masked array related parameters
        if any(_flatten([self.mask])) and hasattr(self.mask, '__iter__'):
            kwds.append(', mask=%s'%repr(self.mask.tolist()))
            
        if self.dtype != None:
            kwds.append(', dtype=%s'%repr(self.dtype))
                
        if self.fill_value != None:
            kwds.append(', fill_value=%s'%repr(self.fill_value))
            
        if self.subok != True:
            kwds.append(', subok=%s'%repr(self.subok))
            
        if self.keep_mask != True:
            kwds.append(', keep_mask=%s'%repr(self.keep_mask))
            
        if self.hard_mask != False:
            kwds.append(', hard_mask=%s'%repr(self.hard_mask))
            
        if len(kwds)>1:
            kwds = ''.join(kwds)
            
        return ('PyvtTbl(%s%s)'%(args,kwds)).replace('\n','')
    
    __add__ = _ptmathmethod('__add__')
    __add__.__doc__ = np.ma.MaskedArray.\
                      __add__.__doc__.replace('masked array', 'PyvtTbl')
    
    __radd__ = _ptmathmethod('__add__')
    __radd__.__doc__ = np.ma.MaskedArray.\
                       __radd__.__doc__.replace('masked array', 'PyvtTbl')

    __sub__ = _ptmathmethod('__sub__')
    __sub__.__doc__ = np.ma.MaskedArray.\
                      __sub__.__doc__.replace('masked array', 'PyvtTbl')
    
    __rsub__ = _ptmathmethod('__rsub__')
    __rsub__.__doc__ = np.ma.MaskedArray.\
                       __rsub__.__doc__.replace('masked array', 'PyvtTbl')

    __pow__ = _ptmathmethod('__pow__')
    __pow__.__doc__ = np.ma.MaskedArray.\
                      __pow__.__doc__.replace('masked array', 'PyvtTbl')

    __mul__ = _ptmathmethod('__mul__')
    __mul__.__doc__ = np.ma.MaskedArray.\
                      __mul__.__doc__.replace('masked array', 'PyvtTbl')
    
    __rmul__ = _ptmathmethod('__mul__')
    __rmul__.__doc__ = np.ma.MaskedArray.\
                       __rmul__.__doc__.replace('masked array', 'PyvtTbl')
    
    __div__ = _ptmathmethod('__div__')
    __div__.__doc__ = np.ma.MaskedArray.\
                      __div__.__doc__.replace('masked array', 'PyvtTbl')
    
    __rdiv__ = _ptmathmethod('__rdiv__')
    __rdiv__.__doc__ = np.ma.MaskedArray.\
                       __rdiv__.__doc__.replace('masked array', 'PyvtTbl')
    
    __truediv__ = _ptmathmethod('__truediv__')
    __truediv__.__doc__ = np.ma.MaskedArray.\
                          __truediv__.__doc__.replace('masked array', 'PyvtTbl')
    
    __rtruediv__ = _ptmathmethod('__rtruediv__')
    __rtruediv__.__doc__ = np.ma.MaskedArray.\
                           __rtruediv__.__doc__.replace('masked array', 'PyvtTbl')
    
    __floordiv__ = _ptmathmethod('__floordiv__')
    __floordiv__.__doc__ = np.ma.MaskedArray.\
                           __floordiv__.__doc__.replace('masked array', 'PyvtTbl')
    
    __rfloordiv__ = _ptmathmethod('__rfloordiv__')
    __rfloordiv__.__doc__ = np.ma.MaskedArray.\
                            __rfloordiv__.__doc__.replace('masked array', 'PyvtTbl')
    
##    __eq__ = _ptmathmethod('__eq__')
##    __ne__ = _ptmathmethod('__ne__')
##    __lt__ = _ptmathmethod('__lt__')
##    __le__ = _ptmathmethod('__le__')
##    __gt__ = _ptmathmethod('__gt__')
##    __ge__ = _ptmathmethod('__ge__')
##
##    copy = _tsarraymethod('copy', ondates=True)
##    compress = _tsarraymethod('compress', ondates=True)
##    cumsum = _tsarraymethod('cumsum', ondates=False)
##    cumprod = _tsarraymethod('cumprod', ondates=False)
##    anom = _tsarraymethod('anom', ondates=False)
##
##    sum = _tsaxismethod('sum')
##    prod = _tsaxismethod('prod')
##    mean = _tsaxismethod('mean')
##    var = _tsaxismethod('var')
##    std = _tsaxismethod('std')
##    all = _tsaxismethod('all')
##    any = _tsaxismethod('any')
##


    
##df = DataFrame()
##df['first']='Roger Bosco Megan John Jane'.split()
##df['last']='Lew Robinson Whittington Smith Doe'.split()
##df['age']=[28,5,26,51,49]
##df['gender']=['male','male','male','female','fem
