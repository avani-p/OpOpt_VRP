
############################################################################
# Model for Optimizing Vehicle Routing problems with
# Perishable Products under Time-window and Quality Requirements
############################################################################



############ Importing Required Python Libraries ############
import json, datetime, time
from ModelFile import *
import matplotlib.pyplot as mpl


############### Result File Generation ################
now = datetime.now() # current date and time
new_folder = 'Results\\Gap_Optimality'+now.strftime("%m%d_%H%M%S")
if not os.path.exists(new_folder): os.mkdir(new_folder)

runtime_min = 60

file_array = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

N = len(file_array)

IsFeasible = [0]*N
SolCount = [0]*N
BestBound = [0]*N
GapOptimality = [0]*N
CurrObjVal = [0]*N

for iter in range(N):
    file_no = str(file_array[iter])
    json_file = open('DataSets\\dataset_'+file_no+'.json')
    data = json.load(json_file)
    result_file = new_folder + '\\Results for ' + file_no + ' node Dataset'

    model = VRP_Model(data,result_file,runtime_min)

    GapOptimality[iter] = model.GapOptimality
    CurrObjVal[iter] = model.CurrObjVal
    
    # 5 min wait between each test if runtime exceeds 30 mins
    if model.RunTime>1800 and file_no!= file_array[-1]: time.sleep(300)

    
mpl.plot(file_array,GapOptimality,'r*')   
mpl.grid(True)    
mpl.title('Gap Optimality vs Number of Nodes')
mpl.xlabel('Nodes #')
mpl.ylabel('Gap Optimality %')
mpl.savefig('gap_optimality.png')
mpl.close()
