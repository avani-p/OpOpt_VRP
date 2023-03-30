
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
og_veh0_cost = int(data['Vehicles']['0']['HiringCost'])
og_veh0_tcost = int(data['Vehicles']['0']['CostPerHour'])
og_veh0_speed = int(data['Vehicles']['0']['Speed'])
N = len(data['Nodes'])

og_demand = [0]*N
for node in range(N):
    og_demand[node] = int(data['Nodes'][str(node)]['Demand'])

## Available Vehicle0 Cost Variations
veh0_cost_array = [300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200]
veh0_tcost_array = [10, 15, 20, 25, 30, 35]
veh0_speed_array = [30, 40, 50, 60, 70]
ex_demand_array = [0, 1, 2, 3]                

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

def Veh0Cost_Sensitivity():
    with open(result_file+'_veh0cost.txt','w') as res:
        print(f'--------------- Vehicle 0 Hiring Cost Sensitivity --------------',file=res)
        Index = len(veh0_cost_array)
        x_axis = np.arange(Index)
        
        for iter in range(Index):
            veh0_cost = veh0_cost_array[iter]
            
            if veh0_cost==og_veh0_cost: 
                CurrObjVal[iter] = og_model.CurrObjVal
                IsFeasible[iter] = og_model.IsFeasible
                Veh_No_Used[iter] = og_model.VehiclesUsed
            else:
                data['Vehicles']['0']['HiringCost'] = veh0_cost
                model = VRP_Model(data,file_name+'_veh0cost_'+str(veh0_cost),runtime_min)
                CurrObjVal[iter] = model.CurrObjVal
                IsFeasible[iter] = model.IsFeasible
                Veh_No_Used[iter] = model.VehiclesUsed
                if model.RunTime>1500: time.sleep(120)

            print(f'Veh0cost = {veh0_cost}',file=res)
            print(f'IsFeasible = {IsFeasible[iter]}',file=res)
            print(f'CurrObjVal = {CurrObjVal[iter]}',file=res)
            print(f'Vehicles Used = {Veh_No_Used[iter]}','\n',file=res)
    
    mpl.plot(veh0_cost_array,CurrObjVal[0:Index],'r--*')
    mpl.plot(og_veh0_cost, og_model.CurrObjVal,'g^',label='Original')       
    PlotSave('Vehicle 0 Hiring Cost','Objective', 'veh0cost')
    
    mpl.bar(x_axis-0.2,column(Veh_No_Used[0:Index],0),width = 0.2, label = 'Veh0')
    mpl.bar(x_axis,column(Veh_No_Used[0:Index],1),width = 0.2, label = 'Veh1')
    mpl.bar(x_axis+0.2,column(Veh_No_Used[0:Index],2),width = 0.2, label = 'Veh2')
    mpl.xticks(x_axis, veh0_cost_array)
    PlotSave('Vehicle 0 Hiring Cost','Vehicles Used', 'veh0cost_veh_no',False)
    ## Restoring k_dash
    data['Vehicles']['0']['HiringCost'] = og_veh0_cost


def Veh0TCost_Sensitivity():
    with open(result_file+'_veh0Tcost.txt','w') as res:
        print(f'--------------- Vehicle 0 Transport Cost Sensitivity --------------',file=res)
        Index = len(veh0_tcost_array)
        x_axis = np.arange(Index)
        
        for iter in range(Index):
            veh0_tcost = veh0_tcost_array[iter]
            
            if veh0_tcost==og_veh0_tcost: 
                CurrObjVal[iter] = og_model.CurrObjVal
                IsFeasible[iter] = og_model.IsFeasible
                Veh_No_Used[iter] = og_model.VehiclesUsed
            else:
                data['Vehicles']['0']['CostPerHour'] = veh0_tcost
                model = VRP_Model(data,file_name+'_veh0tcost_'+str(veh0_tcost),runtime_min)
                CurrObjVal[iter] = model.CurrObjVal
                IsFeasible[iter] = model.IsFeasible
                Veh_No_Used[iter] = model.VehiclesUsed
                if model.RunTime>1500: time.sleep(120)

            print(f'Veh0 Transport Cost = {veh0_tcost}',file=res)
            print(f'IsFeasible = {IsFeasible[iter]}',file=res)
            print(f'CurrObjVal = {CurrObjVal[iter]}',file=res)
            print(f'Vehicles Used = {Veh_No_Used[iter]}','\n',file=res)
    
    mpl.plot(veh0_tcost_array,CurrObjVal[0:Index],'r--*')
    mpl.plot(og_veh0_tcost, og_model.CurrObjVal,'g^',label='Original')       
    PlotSave('Vehicle 0 Transport Cost','Objective', 'vehotcost')
    
    mpl.bar(x_axis-0.2,column(Veh_No_Used[0:Index],0),width = 0.2, label = 'Veh0')
    mpl.bar(x_axis,column(Veh_No_Used[0:Index],1),width = 0.2, label = 'Veh1')
    mpl.bar(x_axis+0.2,column(Veh_No_Used[0:Index],2),width = 0.2, label = 'Veh2')
    mpl.xticks(x_axis, veh0_tcost_array)
    PlotSave('Vehicle 0 Transport Cost','Vehicles Used', 'veh0tcost_veh_no',False)
    ## Restoring k_dash
    data['Vehicles']['0']['CostPerHour'] = og_veh0_tcost


def Veh0Speed_Sensitivity():
    with open(result_file+'_veh0speed.txt','w') as res:
        print(f'--------------- Vehicle 0 Speed Sensitivity --------------',file=res)
        Index = len(veh0_speed_array)
        x_axis = np.arange(Index)
        
        for iter in range(Index):
            veh0_speed = veh0_speed_array[iter]
            
            if veh0_speed==og_veh0_speed: 
                CurrObjVal[iter] = og_model.CurrObjVal
                IsFeasible[iter] = og_model.IsFeasible
                Veh_No_Used[iter] = og_model.VehiclesUsed
            else:
                data['Vehicles']['0']['Speed'] = veh0_speed
                model = VRP_Model(data,file_name+'_veh0speed_'+str(veh0_speed),runtime_min)
                CurrObjVal[iter] = model.CurrObjVal
                IsFeasible[iter] = model.IsFeasible
                Veh_No_Used[iter] = model.VehiclesUsed
                if model.RunTime>1500: time.sleep(120)

            print(f'Veh0cost = {veh0_speed}',file=res)
            print(f'IsFeasible = {IsFeasible[iter]}',file=res)
            print(f'CurrObjVal = {CurrObjVal[iter]}',file=res)
            print(f'Vehicles Used = {Veh_No_Used[iter]}','\n',file=res)
    
    mpl.plot(veh0_speed_array,CurrObjVal[0:Index],'r--*')
    mpl.plot(og_veh0_speed, og_model.CurrObjVal,'g^',label='Original')       
    PlotSave('Vehicle 0 Speed','Objective', 'veh0speed')
    
    mpl.bar(x_axis-0.2,column(Veh_No_Used[0:Index],0),width = 0.2, label = 'Veh0')
    mpl.bar(x_axis,column(Veh_No_Used[0:Index],1),width = 0.2, label = 'Veh1')
    mpl.bar(x_axis+0.2,column(Veh_No_Used[0:Index],2),width = 0.2, label = 'Veh2')
    mpl.xticks(x_axis, veh0_speed_array)
    PlotSave('Vehicle 0 Speed','Vehicles Used', 'veh0speed_veh_no',False)
    ## Restoring k_dash
    data['Vehicles']['0']['Speed'] = og_veh0_speed


def Demand_Sensitivity():
    with open(result_file+'_Demand.txt','w') as res:
        print(f'--------------- Demand Sensitivity --------------',file=res)
        
        Index = len(ex_demand_array)
        x_axis = np.arange(Index)
        
        for iter in range(Index):
            ex_demand = ex_demand_array[iter]
            # Skip if original combination repeats
            if ex_demand==0: 
                CurrObjVal[iter] = og_model.CurrObjVal
                IsFeasible[iter] = og_model.IsFeasible
                Veh_No_Used[iter] = og_model.VehiclesUsed
            
            else:
                for node in range(N):
                    data['Nodes'][str(node)]['Demand'] = og_demand[node]+ex_demand
                
                model = VRP_Model(data,file_name+'_dem_'+str(ex_demand),runtime_min)
                CurrObjVal[iter] = model.CurrObjVal
                IsFeasible[iter] = model.IsFeasible
                Veh_No_Used[iter] = model.VehiclesUsed
                if model.RunTime>1500: time.sleep(120)

            print(f'Extra Demand ={ex_demand}',file=res)
            print(f'IsFeasible = {IsFeasible[iter]}',file=res)
            print(f'CurrObjVal = {CurrObjVal[iter]}',file=res)
            print(f'Vehicles Used = {Veh_No_Used[iter]}','\n',file=res)

    mpl.plot(ex_demand_array,CurrObjVal[0:Index],'r--*')
    mpl.plot(0, og_model.CurrObjVal,'g^',label='Original')       
    PlotSave('Extra Demand','Objective', 'demand')
    
    mpl.bar(x_axis-0.2,column(Veh_No_Used[0:Index],0),width = 0.2, label = 'Veh0')
    mpl.bar(x_axis,column(Veh_No_Used[0:Index],1),width = 0.2, label = 'Veh1')
    mpl.bar(x_axis+0.2,column(Veh_No_Used[0:Index],2),width = 0.2, label = 'Veh2')
    mpl.xticks(x_axis, ex_demand_array)
    PlotSave('Extra Demand','Vehicles Used', 'demand_veh_no',False)

    for node in range(N):
       data['Nodes'][str(node)]['Demand'] =  og_demand[node]

#Veh0Cost_Sensitivity()
Veh0TCost_Sensitivity()
#Veh0Speed_Sensitivity()
#Demand_Sensitivity()
