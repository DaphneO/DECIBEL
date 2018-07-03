from pyvttbl import DataFrame

# dealing with lists is actually easier here
data1 = [10,12,14,15]
data2 = [20,21,23,25]

# instantiate DataFrame object to hold data
df = DataFrame() # inherents a dict

# put data into a DataFrame object
df['data'] = data1+data2

# build dummy code column
df['conditions'] = ['A']*len(data1)+['B']*len(data2)

# visually verify data in DataFrame
print df

# run 1 way analysis of variance
# returns another dict-like object
aov = df.anova1way('data', 'conditions')

# print anova results
print aov

# this is just to show the data in the aov object
print aov.keys()

# calculate omega-squared
aov['omega-sq'] = (aov['ssbn'] - aov['dfbn']*aov['mswn']) / \
                  (aov['ssbn'] + aov['sswn'] + aov['mswn'])

# you can access the results this way
print aov['omega-sq']
print aov['f']
print aov['p']

