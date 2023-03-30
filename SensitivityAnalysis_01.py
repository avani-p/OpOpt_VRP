
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
og_C_q = float(data['QualityPenaltyCost'])
og_C_t = float(data['TimePenaltyCost'])
og_C_d = float(data['PerDriverCost'])


C_q_array = [450, 500, 550, 600, 650, 700, 750,1000]
C_t_array = [30, 35, 40, 45, 50, 55, 60,120]
C_d_array = [300, 325, 350, 375, 400, 425, 450,900]
                
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


def QualityPenaltyCost_Sensitivity():
    with open(result_file+'_quality_penalty_cost.txt','w') as res:
        print(f'--------------- Quality Penalty Cost Sensitivity --------------',file=res)
        Index = len(C_q_array)
        x_axis = np.arange(Index)
        
        for iter in range(Index):
            C_q = C_q_array[iter]
            
            if C_q==og_C_q: 
                CurrObjVal[iter] = og_model.CurrObjVal
                IsFeasible[iter] = og_model.IsFeasible
                Veh_No_Used[iter] = og_model.VehiclesUsed
            else:
                data['QualityPenaltyCost'] = C_q
                model = VRP_Model(data,file_name+'_Cq'+str(C_q),runtime_min)
                CurrObjVal[iter] = model.CurrObjVal
                IsFeasible[iter] = model.IsFeasible
                Veh_No_Used[iter] = model.VehiclesUsed
                if model.RunTime>1500: time.sleep(120)

            print(f'C_q = {C_q}',file=res)
            print(f'IsFeasible = {IsFeasible[iter]}',file=res)
            print(f'CurrObjVal = {CurrObjVal[iter]}',file=res)
            print(f'Vehicles Used = {Veh_No_Used[iter]}','\n',file=res)
    
    mpl.plot(C_q_array,CurrObjVal[0:Index],'r--*')
    mpl.plot(og_C_q, og_model.CurrObjVal,'g^',label='Original')       
    PlotSave('Quality Penalty Cost','Objective', 'quality_penalty_cost')
    
    mpl.bar(x_axis-0.2,column(Veh_No_Used[0:Index],0),width = 0.2, label = 'Veh0')
    mpl.bar(x_axis,column(Veh_No_Used[0:Index],1),width = 0.2, label = 'Veh1')
    mpl.bar(x_axis+0.2,column(Veh_No_Used[0:Index],2),width = 0.2, label = 'Veh2')
    mpl.xticks(x_axis, C_q_array)
    PlotSave('Quality Penalty Cost','Vehicles Used', 'quality_veh_no',False)
    
    ## Restoring C_q
    data['QualityPenaltyCost'] = og_C_q

def TimePenaltyCost_Sensitivity():
    with open(result_file+'_Time_Penalty_Cost.txt','w') as res:
        print(f'--------------- Time Penalty Cost Sensitivity --------------',file=res)
        Index = len(C_t_array)
        x_axis = np.arange(Index)
        
        for iter in range(Index):
            C_t = C_t_array[iter]
            
            if C_t==og_C_t: 
                CurrObjVal[iter] = og_model.CurrObjVal
                IsFeasible[iter] = og_model.IsFeasible
                Veh_No_Used[iter] = og_model.VehiclesUsed
            else:            
                data['TimePenaltyCost'] = C_t
                model = VRP_Model(data,file_name+'_Ct'+str(C_t),runtime_min)
                CurrObjVal[iter] = model.CurrObjVal
                IsFeasible[iter] = model.IsFeasible
                Veh_No_Used[iter] = model.VehiclesUsed
                if model.RunTime>1500: time.sleep(120)

            print(f'C_t = {C_t}',file=res)
            print(f'IsFeasible = {IsFeasible[iter]}',file=res)
            print(f'CurrObjVal = {CurrObjVal[iter]}',file=res)
            print(f'Vehicles Used = {Veh_No_Used[iter]}','\n',file=res)
    
    mpl.plot(C_t_array,CurrObjVal[0:Index],'b--*')
    mpl.plot(og_C_t, og_model.CurrObjVal,'r^',label = 'Original')
    #mpl.ylim((min(CurrObjVal[0:Index])-100),max(CurrObjVal)+100)
    PlotSave('Time Penalty Cost','Objective', 'Time_Penalty_Cost')
    
    mpl.bar(x_axis-0.2,column(Veh_No_Used[0:Index],0),width = 0.2, label = 'Veh0')
    mpl.bar(x_axis,column(Veh_No_Used[0:Index],1),width = 0.2, label = 'Veh1')
    mpl.bar(x_axis+0.2,column(Veh_No_Used[0:Index],2),width = 0.2, label = 'Veh2')
    mpl.xticks(x_axis, C_t_array)
    PlotSave('Time Penalty Cost','Vehicles Used', 'timePenalty_veh_no',False)
    
    ## Restoring C_t
    data['TimePenaltyCost'] = og_C_t

   
def DriverCost_Sensitivity():
    with open(result_file+'_Driver_Cost.txt','w') as res:
        print(f'--------------- Driver Cost Sensitivity --------------',file=res)
        Index = len(C_d_array)
        x_axis = np.arange(Index)

        for iter in range(Index):
            C_d = C_d_array[iter]
            
            if C_d==og_C_d: 
                CurrObjVal[iter] = og_model.CurrObjVal
                IsFeasible[iter] = og_model.IsFeasible
                Veh_No_Used[iter] = og_model.VehiclesUsed            
            else:            
                data['PerDriverCost'] = C_d
                model = VRP_Model(data,file_name+'_Cd'+str(C_d),runtime_min)
                CurrObjVal[iter] = model.CurrObjVal
                IsFeasible[iter] = model.IsFeasible
                Veh_No_Used[iter] = model.VehiclesUsed
                if model.RunTime>1500: time.sleep(120)

            print(f'C_d = {C_d}',file=res)
            print(f'IsFeasible = {IsFeasible[iter]}',file=res)
            print(f'CurrObjVal = {CurrObjVal[iter]}',file=res)
            print(f'Vehicles Used = {Veh_No_Used[iter]}','\n',file=res)
    
    mpl.plot(C_d_array,CurrObjVal[0:Index],'b--*')
    mpl.plot(og_C_d, og_model.CurrObjVal,'r^',label = 'Original')
    PlotSave('Driver Cost','Objective', 'Driver_Cost')
    
    mpl.bar(x_axis-0.2,column(Veh_No_Used[0:Index],0),width = 0.2, label = 'Veh0')
    mpl.bar(x_axis,column(Veh_No_Used[0:Index],1),width = 0.2, label = 'Veh1')
    mpl.bar(x_axis+0.2,column(Veh_No_Used[0:Index],2),width = 0.2, label = 'Veh2')
    mpl.xticks(x_axis, C_d_array)
    PlotSave('Driver Cost','Vehicles Used', 'driver_veh_no', False)
    
    ## Restoring C_d
    data['PerDriverCost'] = og_C_d


QualityPenaltyCost_Sensitivity()
TimePenaltyCost_Sensitivity()
DriverCost_Sensitivity()

