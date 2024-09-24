# -*- coding: utf-8 -*-

# Copyright 2024 Netherlands eScience Center and CML, Leiden University
# Licensed under the Apache License, version 2.0. See LICENSE for details.

"""
Created on Thu Aug 22 18:01:26 2019
@author: amatunilt
"""

#NOTES:
#   This script allows to estimate the material composition (MC) of products using real product datasets in ecoinvent database.
#   See paper: Amatuni, L., Steubing, B., Heijungs, R., Yamamoto, T., & Mogollón, J. M. Deriving material composition of products using life cycle inventory databases. Journal of Industrial Ecology. https://doi.org/10.1111/jiec.13538
#   We highly recommend visiting this paper first for a solid understanding of the implementation of this product composition estimation algorithm.
#   We also suggest first reviewing a simpler and more universal script "pmc algorithm - general.py" for detailed comments for each code line.
#   This script is an extension of that general script tailoring it to perform on the ecoinvent database. 
#   The comments under this script will be rather limited. 

#REQUIREMENTS: 
#   To run this script in Spyder or VS Code we first prepared a separate conda environment with an installed Brightway 2 (not 2.5!) framework and the Activity Browser GUI on top.
#   Installing Activity Browser in a separate conda environment as instructed on the AB website will install Brightway and all the packages needed, so this is a good starting point.  
#   Basic understanding of Pythin and Brightway is required to be able to replicate this code for your own products/materials/LCI database  
#   Reading the paper: Amatuni, L., Steubing, B., Heijungs, R., Yamamoto, T., & Mogollón, J. M. Deriving material composition of products using life cycle inventory databases. Journal of Industrial Ecology. https://doi.org/10.1111/jiec.13538
#   Reviewing explanatory comments under the general script first.

#IMPORTS:
from brightway2 import *
from functools import cmp_to_key
import brightway2 as bw
import json
import csv
import sys
import os

# Get the directory where the script is located and set the current working directory to the script's directory
script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(script_dir)

#CONSTANTS
FLOAT_RND = 5
LAPTOP = 'computer production, laptop'
FRIDGE = 'refrigerator production'
CAR_D = 'passenger car production, diesel'
CAR_P = 'passenger car production, petrol/natural gas'
CAR_E_motor = 'electric motor production, vehicle (electric powertrain)'
SCOOTER_E_motor = 'electric motor production, for electric scooter'
prod_list = [LAPTOP]
prod_wght = [3.15] #kg per product from Ecoinvent 3.6
METHOD_KEY = ('ReCiPe 2016 v1.03, endpoint (H)', 'natural resources', 'material resources: metals/minerals') #selected method from the list of impact methods; in practice arbitrary as it does not impact the resulting inventory/supply vectors but is needed to run the lca.lci() command
BIO_MAT_LIST = ["Copper", "Aluminium", "Tantalum"] #the natural materials of interest (the appropariate flows in the biospere database will be selected later on based on this names). Each name should start with the capital letter (see conventional names of materials/metals in the biosphere3 database)
FU = 1 #amount of the functional unit
FILE_OUT = 'output.txt'
KEY_index = 1 #index of the actual activity/bioflow key in a conventional tuple key like (db, key)
DB_NAME = 'ecoinvent-3.10-cutoff' #'consequential310'

#PREPARATIONS:
#bw2setup() #set up the Brightway2 environment (if not already set up)
#assumed that you already have default bw env and ecoinvent database that is called 'consequential310' - change if needed
projects.set_current("default")
db  = bw.Database(DB_NAME)
bio = bw.Database('biosphere3')

#DEFINE AVOID LISTS
avoid_activities = ["treatment", "water", "waste", "container", "box", "packaging", "foam", "electricity", "factory", "adapter", "oxidation", "construction", "heat", "facility", "gas", "freight", "mine", "infrastructure", "conveyor", "road", "building", "used", "maintenance", "transport", "moulding", "mold", "wastewater", "steam", "scrap", "converter"]
    
#MATERIAL SELECTION
#hint: use markets instead of production activities as they conveniently include all the regional prod. activities and there's no need to list them separately
materials_dict_cutoff310 = {
        "Metals":
            {BIO_MAT_LIST[0]: [(DB_NAME, 'bc9651dcc7c9e1666633deebe9cc51ba')],
             BIO_MAT_LIST[1]: [(DB_NAME, 'e540cdb4add7b620e2d2d64a3abb418d'), (DB_NAME, '56a38ae7dd7648bab5997fab280bbf46')] #market for aluminium, cast alloy + market for aluminium, wrought alloy 
            }
}

#import materials_dict from JSON
with open('dict_gen/plastics_dict_ecoinvent-3.10-cutoff_m.json', 'r') as fp:
    materials_dict_cutoff310["Plastics"] = json.load(fp) 
#flatten all tuples under 'Metals' into a single list
combined_plastics = [item for sublist in materials_dict_cutoff310["Plastics"].values() for item in sublist]
materials_dict_cutoff310["Plastics"] = {"Total": combined_plastics}

#FUNCTIONS:
def activity_by_name(name, db): #return first activity dataset based on name keyword
    candidates = [x for x in db if name in x['name']]
    candidates = sorted(candidates, key=cmp_to_key(lambda item1, item2: len(item1['name']) - len(item2['name'])))  #shortest name is the best match
    with open(FILE_OUT, 'a') as f:
        print('\n', candidates[0], ' from ', db.name, file=f)
    return candidates[0]

def activity_by_key(key, db): # key = tuple(db, key) -> activity (dataset) in db
    return db.get(key[1])

#List all intermediate (technosphere) flows (activities) in the resulting supply-array (see the Paper) that is stored in the reuslting 'lca' object
def list_techno_inventory(lca):
    print("\u25A0 Supply array: ")
    for k in lca.activity_dict:
        print(activity_by_key(k, db)["name"], ": ", lca.supply_array[lca.activity_dict[k]])
    print()

#For the product of interest from the database 'db' list incorporation parameters for all inputs of its production process
def product_inputs(prod, db):
    act = activity_by_name(prod, db)
    for exc in act.technosphere():
        try:
            print(bw.get_activity(exc["input"])._document.product, exc['incorporated'])
        except: 
            print('Error: Not all of the exchanges in your LCI database have the incorporation parameter assigned!')
            sys.exit(1) 

#Resets inc. parameter in the original db (~30 min)
def db_inc_filter(db, avoid_activities):
    i = 0
    prt = -1
    for act in db:
        # update the bar
        i += 1
        pr = int(100*i/len(db))
        if  (pr != prt):
            b = "\rAssigning material incorporation parameters to all exchanges in the " + db.name + " database: " + str(pr) + "%"
            print (b, end="\r")
            prt = pr
        for exc in act.technosphere():
            avoid = False
            in_act = bw.get_activity(exc["input"])
            exc_name = in_act._document.product #product name; same as exc["name"] but works for manual db
            for word in avoid_activities:
                if word in exc_name: #name of the product of the exchange
                    avoid = True
                    break
            exc['incorporated'] = 0.0 if avoid else 1.0
            exc.save()
    print('\n')

#Restores all the incorporation parameters in the database back to 1
def db_inc_reset(db): 
    i = 0
    prt = -1
    for act in db:
        # update the bar
        i += 1
        pr = int(100*i/len(db))
        if  (pr != prt):
            b = "\rApplying full (1.0) incorporation parameters to the activities: " + str(pr) + "%"
            print (b, end="\r")
            prt = pr
        for exc in act.technosphere():
            exc['incorporated'] = 1.0
            exc.save()
    print('\n')  
            
#Edits lca techn. matrix (exclude non-incorporative exc) based on incorporation parameter in the db database
def lca_exclude_noninc(db, lca): 
    i = 0
    prt = -1
    print('\n')
    for act in db:
        # update the bar
        i += 1
        pr = int(100*i/len(db))
        if  (pr != prt):
            b = "\rExcluding the non-incorporated materials from the technosphere matrix: " + str(pr) + "%"
            print (b, end="\r")
            prt = pr
        for exc in act.technosphere():
            try:
                inc = exc['incorporated']
            except:
                inc = 1 #if the incorporation parameter was not entered in ab or set by db_inc_filter() previously
                print('Error: missing incorporation parameter in the LCI database detected! -> assigned to 1')
            if  inc < 1:
                row = lca.activity_dict[exc["input"]]
                col = lca.activity_dict[act.key]
                lca.technosphere_matrix[row, col] *= inc
    return lca

#Creates an LCA object based on the reference product 'act' in the database 'db' and the bioflow 'material_bioflow' of interest     
def LCA_create(act, FU): 
    functional_unit = {act: FU}
    return bw.LCA(functional_unit, METHOD_KEY)

#'prod' is passed for a proper relative weight calculation
def materials_inv(mat_list, lca, prod): 
    for flow_index, amount in enumerate(lca.inventory.sum(axis=1).flat): # lca.inventory.sum(axis=1).flat gives you the summed inventory for each biosphere flow
        flow_key = list(lca.biosphere_dict.items())[flow_index][0][KEY_index] #obtain key of each bioflow (in the resulting 'inventory') based on the 'biosphere_dict' that lists the keys of the resulting elementary flows 
        flow_name = bio.get(flow_key)['name'] #obtain name of each bioflow using its key based on the 'bio' database that contains the names of all elementary flows
        if flow_name in mat_list:
            print(f'{flow_name}: {round(amount, FLOAT_RND)} kg OR {round(amount/prod_wght[prod_list.index(prod)] * 100, FLOAT_RND)} %')  
    print('\n')
    return 0

#Given predefined 'materials_dict' (see above), aggregates and prints 
# resulting material fllows (MC or MF of a product, depending if filtering was applied) 
# using the 'supply_array' from the resulting 'lca' object
def materials_sup(materials_dict, lca, prod):
    try:
        for material_group in materials_dict:
            gr_sum = 0
            for material in materials_dict[material_group]:
                mat_sum = 0
                for act_key in materials_dict[material_group][material]:
                    act_key = tuple(act_key) #this fix to is needed as the keys from the fp file are given as a list [db_name,key]
                    mat_sum += lca.supply_array[lca.activity_dict[act_key]]
                print(material, " : ", round(mat_sum, FLOAT_RND), ' kg')
                gr_sum += mat_sum
            print(f'> {material_group} total : {round(gr_sum, FLOAT_RND)} kg OR {round(gr_sum/prod_wght[prod_list.index(prod)] * 100, FLOAT_RND)} %')
    except Exception as e: 
        print(f'\nError: most likely you used a wrong key in your material dictionary that does not properly link to the activity in the LCI database! \nCheck the {e}')
        sys.exit(1) 
    return 0

def db_amount_save(db): #save all the original amounts of the exchanges
    for act in db:
        for exc in act.technosphere():
            exc['amount_save'] = exc['amount']
            exc.save()
            
def db_amount_restore(db): #restore all the original amounts of the exchanges
    for act in db:
        for exc in act.technosphere():
            exc['amount'] = exc['amount_save']
            exc.save()
            
def db_inc_to_amounts(db): #adjust all the amounts of the exchanges based on the incorporation
    for act in db:
        for exc in act.technosphere():
            exc['amount'] = exc['amount_save'] * exc['incorporated']
            exc.save()    

def db_to_csv(db): #save datasets (name, key) into the csv file
    #generate a list of act. names and their keys
    list = [['name','key']]
    for act in db:
        list.append([act["name"], act.key[1]])
    #write into csv
    with open(db.name+'.csv', 'w') as f:
        writer = csv.writer(f, delimiter='|', lineterminator="\n")
        writer.writerows(list)
    return str(db) + " saved into " + db.name + '.csv'

#MAIN CODE:

#Run through ecoinvent activities and assign material incorporation parameter (from 0 to 1) to each exchange based on the list of keywords in the 'avoid_activities' list of keywords
#db_inc_filter(db, avoid_activities) 

print(combined_plastics)

#lists description of each inout ('exc') in the activity 'act': key, name, amount, unit, CPC code, etc
#for exc in act.technosphere():
#    print(exc.as_dict())

#For each product of interest, list it MF (material footprint) and MC (material composition) after technosphere filtering 
for prod in prod_list:
    act = activity_by_name(prod, db)
    lca = LCA_create(act, FU)
    lca.lci() #creates technosphere

    print("\n>>> BEFORE filtering:\n")
    print(f'\u25A0 Material footprint, MF (based on inventory vector) in {FU} {act}:')
    materials_inv(BIO_MAT_LIST, lca, prod)
    print("\u25A0 Material footprint, MF (based on supply array):")
    materials_sup(materials_dict_cutoff310, lca, prod) 

    lca_exclude_noninc(db, lca) #edit matrix (technosphere)
    lca.lci_calculation()

    print("\n>>> AFTER filtering:\n")
    print(f'\u25A0 Material composition, MC (based on inventory vector) in {FU} {act}:')
    materials_inv(BIO_MAT_LIST, lca, prod)
    print("\u25A0 Material composition, MC (based on supply array):")
    materials_sup(materials_dict_cutoff310, lca, prod)
        
print('DONE')