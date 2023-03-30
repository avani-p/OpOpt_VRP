############################################################################
# Model for Optimizing Vehicle Routing problems with
# Perishable Products under Time-window and Quality Requirements
############################################################################



############ Importing Required Python Libraries ############
import json, datetime
from ModelFile import *


# Import the json file 
file_no = input('Dataset file number (after \"_\"): ')
json_file = open('DataSets\\dataset_'+file_no+'.json')
data = json.load(json_file)

result_file = 'Results\\Test_Run\\Results_' + file_no + '_node_Dataset'
model = VRP_Model(data,result_file,60)

IsFeasible= model.IsFeasible
SolCount= model.SolCount
BestBound= model.BestBound
GapOptimality = model.GapOptimality
CurrObjVal = model.CurrObjVal

print('Model Run Complete.')
if IsFeasible:
    print('Feasible Model: Z = ',CurrObjVal)
    print('Result File Generated.')
else:
    print('InFeasible Model!!!!')
    print('Result File NOT Generated.')