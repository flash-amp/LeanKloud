# -*- coding: utf-8 -*-
"""
Created on Tue May 18 12:24:37 2021

*This code works for csv file supplied as follows:

Column 1 as names,
other columns as subject marks,
and their corresponding column names must be specified

@author: Azeez
"""
#Using pandas dataframe for ease of use
import pandas as pd

#prints the list values passed with comma separated
def print_names(names):
  print(*names[y], sep = ", ")

#returns topper student details of subject passed
def high_score(sub):
  return data[data[sub] == data[sub].max()]

#prints in the specified
def print_topper(names,sub):
  sp = ['s','are'] if(len(names)>1) else ['','is']
  print('\nTopper'+sp[0]+' in '+sub+' '+sp[1]+' : ',end='')
  print_names(names)

#getting the input file to the code
data = pd.read_csv(r'C:/Users/Azeez/Downloads/Untitled Folder/Student_marks_list.csv')

#getting all the column names
x = list(data.columns)

#popping the first column_name mostly it is names
y = x.pop(0)

'''
Looping to print the toppers based on marks
Creating a new column value for total calculation
'''
for i in range(len(x)): 
  print_topper(high_score(x[i]),x[i])
  if(i == 0):
    data['Total'] = data[x[i]] 
  else:
    data['Total'] += data[x[i]] 
    
#Getting the top 3 students using sort..
best_3 = data.sort_values(by=['Total'] , ascending = False).head(3)
print("\nBest Students in the class are :",end=' ')
print_names(best_3)

print("\nTime complexity : O(n), where n is no. of subjects")