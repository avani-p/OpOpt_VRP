
############################################################################
# Model for Optimizing Vehicle Routing problems with
# Perishable Products under Time-window and Quality Requirements
############################################################################



############ Importing Required Python Libraries ############
import json, datetime, time
from ModelFile import *
import matplotlib.pyplot as mpl
import numpy as np 

# Import the json file 
file_no = input('Dataset file number (after \"_\"): ')
json_file = open('DataSets\\dataset_'+file_no+'.json')
data = json.load(json_file)


############### Result File Generation ################
now = datetime.now() # current date and time
new_folder = 'Results\\Sensitivity_'+file_no+'_'+now.strftime("%m%d_%H%M%S")
if not os.path.exists(new_folder): os.mkdir(new_folder)
result_file = new_folder+'\\sensitivity_dataset'+file_no+'_'+now.strftime("%m%d_%H%M%S")
file_name = new_folder+'\\Results for '+file_no+' node Dataset'

runtime_min = 60
N = 10

IsFeasible = [0]*N
CurrObjVal = [0]*N
Veh_No_Used = [[0 for x in range(len(data['Vehicles']))] for y in range(N)] 

## Run Original Model

og_model = VRP_Model(data,file_name,runtime_min)
og_k_dash = float(data['DecayRate'])
og_q_dash = float(data['MinAcceptableQuality'])

T = len(data['Vehicles'])

og_veh_no = [0]*T
for type in range(T):
    og_veh_no[type] = int(data['Vehicles'][str(type)]['Number'])

## Decay Rate Variations
k_dash_array = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10]
## Minimum Acceptable Variations
q_dash_array = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
## Available Vehicle Number Variations
VehNo_array = [0, 1, 2, 3, 4]
                
def column(matrix, i):
    return [row[i] for row in matrix]

def PlotSave(X_tag,Y_tag, plot_type,grid_on = True):
    mpl.title(Y_tag+' v/s '+ X_tag)
    mpl.grid(grid_on)
    mpl.legend(loc = 'best')
    mpl.xlabel(X_tag)
    mpl.ylabel(Y_tag)
    mpl.savefig(result_file+'_'+plot_type+'.png')
    mpl.close()


def DecayRate_Sensitivity():
    with open(result_file+'_decay.txt','w') as res:
        print(f'--------------- Decay Rate Sensitivity --------------',file=res)
        Index = len(k_dash_array)
        x_axis = np.arange(Index)
        
        for iter in range(Index):
            k_dash = k_dash_array[iter]
            
            if k_dash==og_k_dash: 
                CurrObjVal[iter] = og_model.CurrObjVal
                IsFeasible[iter] = og_model.IsFeasible
                Veh_No_Used[iter] = og_model.VehiclesUsed
            else:
                data['DecayRate'] = k_dash
                model = VRP_Model(data,file_name+'_k'+str(k_dash),runtime_min)
                CurrObjVal[iter] = model.CurrObjVal
                IsFeasible[iter] = model.IsFeasible
                Veh_No_Used[iter] = model.VehiclesUsed
                if model.RunTime>1500: time.sleep(120)

            print(f'k_dash = {k_dash}',file=res)
            print(f'IsFeasible = {IsFeasible[iter]}',file=res)
            print(f'CurrObjVal = {CurrObjVal[iter]}',file=res)
            print(f'Vehicles Used = {Veh_No_Used[iter]}','\n',file=res)
    
    mpl.plot(k_dash_array,CurrObjVal[0:Index],'r--*')
    mpl.plot(og_k_dash, og_model.CurrObjVal,'g^',label='Original')       
    PlotSave('Decay Rate','Objective', 'decay')
    
    mpl.bar(x_axis-0.2,column(Veh_No_Used[0:Index],0),width = 0.2, label = 'Veh0')
    mpl.bar(x_axis,column(Veh_No_Used[0:Index],1),width = 0.2, label = 'Veh1')
    mpl.bar(x_axis+0.2,column(Veh_No_Used[0:Index],2),width = 0.2, label = 'Veh2')
    mpl.xticks(x_axis, k_dash_array)
    PlotSave('Decay Rate','Vehicles Used', 'decay_veh_no',False)
    ## Restoring k_dash
    data['DecayRate'] = og_k_dash

def MinQuality_Sensitivity():
    with open(result_file+'_minQuality.txt','w') as res:
        print(f'--------------- Min Acceptable Quality Sensitivity --------------',file=res)
        Index = len(q_dash_array)
        x_axis = np.arange(Index)
        
        for iter in range(Index):
            q_dash = q_dash_array[iter]
            
            if q_dash==og_q_dash: 
                CurrObjVal[iter] = og_model.CurrObjVal
                IsFeasible[iter] = og_model.IsFeasible
                Veh_No_Used[iter] = og_model.VehiclesUsed
            else:        
                data['MinAcceptableQuality'] = q_dash
                model = VRP_Model(data,file_name+'_q'+str(q_dash),runtime_min)
                CurrObjVal[iter] = model.CurrObjVal
                IsFeasible[iter] = model.IsFeasible
                Veh_No_Used[iter] = model.VehiclesUsed
                if model.RunTime>1500: time.sleep(120)

            print(f'q_dash = {q_dash}',file=res)
            print(f'IsFeasible = {IsFeasible[iter]}',file=res)
            print(f'CurrObjVal = {CurrObjVal[iter]}',file=res)
            print(f'Vehicles Used = {Veh_No_Used[iter]}','\n',file=res)
    
    mpl.plot(q_dash_array,CurrObjVal[0:Index],'b--*')
    mpl.plot(og_q_dash, og_model.CurrObjVal,'r^',label = 'Original')
    PlotSave('Min Acceptable Quality','Objective', 'minQuality')
    
    mpl.bar(x_axis-0.2,column(Veh_No_Used[0:Index],0),width = 0.2, label = 'Veh0')
    mpl.bar(x_axis,column(Veh_No_Used[0:Index],1),width = 0.2, label = 'Veh1')
    mpl.bar(x_axis+0.2,column(Veh_No_Used[0:Index],2),width = 0.2, label = 'Veh2')
    mpl.xticks(x_axis, q_dash_array)
    PlotSave('Min Acceptable Quality','Vehicles Used', 'minQuality_veh_no',False)
    
    ## Restoring q_dash
    data['MinAcceptableQuality'] = og_q_dash



def VehNo_Sensitivity():
    with open(result_file+'_VehNo.txt','w') as res:
        print(f'--------------- Vehicle Number Sensitivity --------------',file=res)
        
        Index = len(VehNo_array)

        ObjValue = [[0 for x in range(Index)] for y in range(T)] 
        Feasibility= [[0 for x in range(Index)] for y in range(T)] 
        
        for type in range(T):
            for iter in range(Index):
                veh_no = VehNo_array[iter]
                # Skip if original combination repeats
                if veh_no==og_veh_no[type]: 
                    ObjValue[type][iter] = og_model.CurrObjVal
                    Feasibility[type][iter] = model.IsFeasible

                else:
                    data['Vehicles'][str(type)]['Number'] = veh_no
                    new_name = file_name+'_veh'+str(type)+'_'+str(iter)
                    model = VRP_Model(data,new_name,runtime_min)
                    ObjValue[type][iter] = model.CurrObjVal
                    Feasibility[type][iter] = model.IsFeasible
                    if model.RunTime>1500: time.sleep(120)

                print(f'Type:{type} veh_no ={veh_no}',file=res)
                print(f'IsFeasible = {Feasibility[type][iter]}',file=res)
                print(f'CurrObjVal = {ObjValue[type][iter]}','\n',file=res)

            ## Restoring Vehicle Number
            data['Vehicles'][str(type)]['Number'] = og_veh_no[type]

    markers = ['r--o','b-.v','g-x','m-^','c-+','s-teal']
    for type in range(T):
        mpl.plot(VehNo_array,ObjValue[type][:],markers[type],label='Type '+str(type))
        mpl.plot(og_veh_no[type], og_model.CurrObjVal,'*',label = 'Type '+str(type)+' Original')
    
    PlotSave('Vehicle No','Objective', 'VehNo')



DecayRate_Sensitivity()
MinQuality_Sensitivity()
VehNo_Sensitivity()
