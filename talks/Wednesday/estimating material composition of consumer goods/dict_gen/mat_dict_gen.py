# -*- coding: utf-8 -*-

# Copyright 2021 Netherlands eScience Center and CML, Leiden University
# Licensed under the Apache License, version 2.0. See LICENSE for details.

"""
Created on Wed Oct  9 08:47:41 2019

@author: yamamototm
"""

import json
import pandas as pd
import os
import sys
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# Get the directory where the script is located and set the current working directory to the script's directory
script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(script_dir)

#Const
file_name = 'plastics'
db_name = 'ecoinvent-3.10-cutoff'
LIMIT_SCORE = 100
PET_CORRECT = True

#reading
ei = pd.read_csv(db_name+'.csv', sep='|', encoding="cp1252")
material_group = pd.read_excel(file_name+'.xlsx')

def checker(wrong_options, correct_options):
    names_array = []
    ratio_array = []    
    i = 0
    prt = -1
    for wrong_option in wrong_options:
        #if wrong_option in correct_options:
         #  names_array.append(wrong_option)
          # ratio_array.append(100)
        #else:   
            # update the bar
            i += 1
            pr = int(100*i/len(wrong_options))
            if  (pr != prt):
                b = "\rScanning for the appropriate activities in " + file_name + ": " + str(pr) + "%"
                print (b, end="\r")
                prt = pr
                
            x = process.extractOne(wrong_option, correct_options, scorer = fuzz.partial_ratio)
            names_array.append(x[0])
            ratio_array.append(x[1])
            
    return names_array, ratio_array

#correct for PET as they classified as PE:
def PET_correct(df):
    df1 = df[df['plastic_name']=='polyethylene'].reset_index(drop=True)
    df2 = df[df['plastic_name']!='polyethylene'].reset_index(drop=True)
    names_array = []
    for item in df1['ei_name'].tolist():
        if 'terephthalate' in item:
            names_array.append('polyethylene terephthalate')
        
        else:
            names_array.append('polyethylene')
    df1['plastic_name'] = pd.Series(names_array)
    return pd.concat((df1,df2), axis=0)

strOptions = material_group['Name'].tolist()
str2Match = ei['name'].tolist()

name_match, ratio_match = checker(str2Match, strOptions)

df = pd.DataFrame()
df['ei_name'] = pd.Series(str2Match)
df['plastic_name'] = pd.Series(name_match)
df['correct_ratio'] = pd.Series(ratio_match)
df['key'] = ei['key']

#select markets
df = df[df["ei_name"].str.contains('market')]

#filter our unrelated activities
df = df[df['correct_ratio'] == LIMIT_SCORE][['ei_name','plastic_name','key']]
df = df[df['ei_name'] != 't'] #remove this activity

if PET_CORRECT:
    df = PET_correct(df)

df_t = df
#get the symbol
df = pd.merge(df, material_group, how='inner', left_on='plastic_name', right_on='Name')
df = df[['key','Symbol']]

df['db'] = db_name

df_dict = df.groupby('Symbol')[['db','key']].apply(lambda g: tuple(map(tuple, g.values.tolist()))).to_dict()


# dictionary in the end        
        
# use fuzzy wuzzy to classify all product list according to this table
# check how many and if it is feasible to do it manually (~400 maybe?)
# so two exceptions + PET
# remove markets
# generate the dictionary

#save dict. to JSON file
with open(file_name+'_dict_'+db_name+'_m.json', 'w') as fp:
    json.dump(df_dict, fp)





