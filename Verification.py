############################################################################
# Model for Optimizing Vehicle Routing problems with
# Perishable Products under Time-window and Quality Requirements
############################################################################



############ Importing Required Python Libraries ############
import json, datetime, time
from ModelFile import *
import matplotlib.pyplot as mpl

# Use the 4 node dataset

for file_no in ['4','5','6']:

#file_no = str(4)
    json_file = open('DataSets\\dataset_'+file_no+'.json')
    data = json.load(json_file)

    ############### Result File Generation ################
    new_folder = 'Results\\Verification'
    if not os.path.exists(new_folder): os.mkdir(new_folder)
    result_file = new_folder + '\\Verification Results for ' + file_no + ' node Dataset'

    ## Run Original Model
    model = VRP_Model(data, result_file, 60)
    ##CurrObjVal = validation_model.CurrObjVal
    ##IsFeasible = validation_model.IsFeasible
    ##if validation_model.RunTime>1500: time.sleep(120)

