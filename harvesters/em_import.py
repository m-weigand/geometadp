from emagpy import Problem

k = Problem() # this create the main object
k.createSurvey(name) # this import the data
k.invert(forwardModel='CS') # specify the forward model (here the Cumulative Sensitivty of McNeil1980)
k.showResults() # display the section

# em metadata 2 collect

# on file
# date creation
# date modified
# filename

# file type
# extension
# instrument

# data
# units
# number of collumns
# collumns headers
# number of lines

