
############################################################################
# Model for Optimizing Vehicle Routing problems with
# Perishable Products under Time-window and Quality Requirements
############################################################################


############ Importing Required Python Libraries ############
from math import *
import gurobipy as gp
import matplotlib.pyplot as mpl
import warnings, os
from datetime import datetime


# setting ignore as a parameter and further adding category
warnings.filterwarnings(action='ignore', category=UserWarning)


############### Define Class ####################
class VRP_Model:
    ## Function for calling the class
    def __init__(self,data, result_file, run_time_minutes=180):
        
        ################ Create a new model #########################
        model = gp.Model()

        ######################### Parameters ########################
        Nodes = data['Nodes']
        # Number of Nodes
        N = len(Nodes)

        # Empty List for Demand
        D = [None]*N
        # Empty List for Allowable Time Withput Penalty
        L_a = [None]*N
        # Empty List for Latest Time of Reciept
        L= [None]*N
        # Empty List for X-coordinates
        X= [None]*N
        # Empty List for Y-coordinates
        Y= [None]*N

        # Retrieve data from Json for Each Node
        for a in range(N):
            node_key = str(a)
            # Demand for Node a
            D[a] = float(Nodes[node_key]['Demand'])
            # Allowable Time without Penalty for Node a
            L_a[a] = float(Nodes[node_key]['AllowedTime'])
            # Latest Time of Reciept for Node a
            L[a] = float(Nodes[node_key]['LatestTime'])
            # X-coordinate of Node N
            X[a] = float(Nodes[node_key]['X'])
            # Y-coordinate of Node N
            Y[a] = float(Nodes[node_key]['Y'])


        # N * N empty marix of distance 
        d = [[0 for x in range(N)] for y in range(N)] 

        # Calculate Distance Between Nodes a & b (in km)
        for a in range(N):
            d[a][a]=0
            for b in range(a+1,N):
                val = sqrt(pow(X[a]-X[b], 2) + pow(Y[a]-Y[b],2))
                # Limiting the value to 2 decimals
                d[a][b] = round(val,2)
                d[b][a] = d[a][b]


        Vehicles = data['Vehicles']
        # Types of Vehicles
        T = len(Vehicles)


        # Empty List for Number
        V = [0]*T
        # Empty List for Capacity
        P = [0]*T
        # Empty List for Speed
        v= [0]*T
        # Empty List for Cost for Hiring
        C_h= [0]*T
        # Empty List for Cost for Transportation
        C_t= [0]*T

        # Retrieve data from Json for Each Type of Vehicle
        for a in range(T):
            veh_key = str(a)
            # Number of Vehicle Type a
            V[a] = int(Vehicles[veh_key]['Number'])
            # Capacity of Vehicle Type a
            P[a] = float(Vehicles[veh_key]['Capacity'])
            # Speed of Vehicle Type a (km/h)
            v[a] = float(Vehicles[veh_key]['Speed'])
            # Hiring Cost of Vehicle Type a
            C_h[a] = float(Vehicles[veh_key]['HiringCost'])
            #Transportation cose per hour of Vehicle Type a
            C_t[a] = float(Vehicles[veh_key]['CostPerHour'])

        # Rate of Decay/Degradation in product quality
        k_dash = float(data['DecayRate'])

        # Minimum acceptable quality
        q_dash = float(data['MinAcceptableQuality'])

        # Penalty cost per unit of product per unit time for being late than the allowed time
        C_p = float(data['TimePenaltyCost'])
        
        # Devalued cost per unit product due to quality lost
        C_q = float(data['QualityPenaltyCost'])
        
        # Cost of hiring a driver
        C_d = float(data['PerDriverCost'])
        
        
        ######################## Check Capacity ###########
        # cap_total = sum(P)
        cap_total = sum(a * b for a, b in zip(P, V))
        demand_total = sum(D)       
        
        ########################### Create variables ##################
        M = 1000
        V_max = max(V)
        max_x = max(max(X), abs(min(X)))
        max_y = max(max(Y), abs(min(Y)))

        A1 = [(m,n,i,j) for m in range(T) for n in range(V_max) for i in range(N) for j in range(N)]
        A2 = [(m,n,j) for m in range(T) for n in range(V_max) for j in range(N)]

        ################### Decision variables #######################
        p = model.addVars(N, vtype=gp.GRB.BINARY, name="arrived late")
        q = model.addVars(N, vtype=gp.GRB.CONTINUOUS, name="quality at arrival")
        t = model.addVars(N, vtype=gp.GRB.CONTINUOUS, name="time of arrival") ## time in hours
        x = model.addVars(A1, vtype=gp.GRB.BINARY, name="vehicle type m vehicle number n going from i to j")
        w = model.addVars(A2, vtype=gp.GRB.INTEGER, name="number of products left in vehicle type m after node j")  
        r = model.addVars(T, vtype=gp.GRB.INTEGER, name="how many vehicles of type m are going out")
       
       
        ################# Set objective function ####################

        flag = 1
        Z = 0
        for m in range(T):
            # Cost of hiring a vehicle and driver
            Z = Z + (C_h[m] + C_d)*r[m]
            for n in range(V[m]):
                for i in range(N):
                    for j in range(N): 
                        # Cost of transportation
                        Z = Z + (d[i][j]/v[m])*C_t[m]*x[m,n,i,j]
                        if j >= 1 and flag == 1:
                            # Penalty cost due to Quality Decay and Late Arrival
                            Z = Z + C_q*(1-q[j])*D[j] + (t[j] - L_a[j]) * C_p*p[j]*D[j] 
                    flag = 0

        model.setObjective(Z, gp.GRB.MINIMIZE)

        #################### Add constraints ########################

        # Constraint that the product quality level is the best 
        # when it is dispatched from the warehouse for distribution
        model.addConstr(q[0] == 1)
        model.addConstr(t[0] == 0)

        for m in range(T):
            
            # Constraint finds out the total number of a type 
            # of vehicles put into use. 
            model.addConstr(sum(x[m,n,0,j] for n in range(V_max) for j in range(1,N)) == r[m])
            model.addConstr(r[m] <= V[m])

            for n in range(V_max):
                # Constraint represents the total number of units of
                # the product in a vehicle once it departs from the warehouse
                model.addConstr(w[m,n,0] <= P[m])
                
                # Constraint ensures that the vehicle departs the warehouse with
                # units atleast equal to demand of nodes it visits
                model.addConstr(w[m,n,0] == sum((D[j]*x[m,n,i,j]) for i in range(N) for j in range(N) ))
            
                for i in range(N):
                    if n >= V[m]:
                        model.addConstr(w[m,n,i] ==0)
                                
                    for j in range(1,N):
                            # Contraint for resulting quality of the product 
                            # arriving at a retail store.
                            model.addConstr(q[j] <= q[i] - (t[j])*k_dash + M*(1 - x[m,n,i,j]))

                            # Constraint that finds the time of arrival 
                            # of the product at a retail store
                            model.addConstr(t[j] >= t[i] + (d[i][j]/v[m]) - M*(1 - x[m,n,i,j])) 
                            
                            # constraint determines the number of units of 
                            # the product left after a retail store has been served -- Sandwich Constraints
                            model.addConstr(w[m,n,j] >= (w[m,n,i] - D[j]) - M*(1- x[m,n,i,j]))
                            model.addConstr(w[m,n,j] <= (w[m,n,i] - D[j]) + M*(1- x[m,n,i,j]))
                            
                            if n >= V[m]:
                                model.addConstr(x[m,n,i,j] ==0)
                                
                

        for j in range(1,N):
            
            # Constrain ensure the product’s final quality reaching 
            # retail store is greater than the minimum specified quality level. 
            model.addConstr(q[j] >= q_dash)
            # Redundant Constraint that reduced computation time.
            model.addConstr(q[j] <= q[0])

            # constraint makes sure that this arrival time must be 
            # within the latest time for the receipt of the product. 
            model.addConstr(t[j] <= L[j])

            # Constraint is used in determining whether 
            # a vehicle is reaching a node in time or not.
            # EITHER - OR CONSTRAINT 
            model.addConstr(t[j] - L_a[j] - p[j]*M <= 0)
            model.addConstr( -t[j] + L_a[j] - M + p[j]*M <= 0)

            # Constraint ensures that a retail store is visited by only one
            # vehicle of any of the available types. 
            model.addConstr(sum(x[m,n,i,j] for m in range(T) for n in range(V_max) for i in range(N)) == 1)


        for m in range(T):
            for n in range(V_max):
                for j in range(N):
                    # Constraint makes sure that the total number of units of product
                    # remaining in any vehicle after serving any node cannot be negative
                    model.addConstr(w[m,n,j] >= 0)
                    
                    # Constraint takes care of flow conservation to ensure that 
                    # every vehicle reaching a node must also leave it. 
                    model.addConstr(sum(x[m,n,i,j] for i in range(N)) == sum(x[m,n,j,i] for i in range(N)))
                    
                    # Constraint makes sure that the travel for same not does not contribute
                    model.addConstr(x[m,n,j,j]==0 )

        
        ################## Solve it! ##################### 
        run_time = run_time_minutes * 60       
        model.setParam('TimeLimit', run_time)
        model.optimize()

        ########################### Get Model Characteristics ###############################
        self.IsFeasible = (model.SolCount>0)
        self.SolCount = model.SolCount
        self.RunTime = model.Runtime
        ################ Exit if the model is infeasible #################
        if self.IsFeasible:
            
            gap = (model.MIPGap)*100 # Gap Percentage
            best_z = model.ObjBound

            ################################# Getting Results ###################################

            opt_Z = model.objVal

            opt_p = [0]*N
            opt_q = [0]*N
            opt_t = [0]*N
            opt_r = [0]*T
            opt_x = [[[[0 for j in range(N)] for i in range(N)] for n in range(V_max)] for m in range(T)]
            opt_w = [[[0 for j in range(N)] for n in range(V_max)] for m in range(T)]

            for m in range(T):
                opt_r[m] = round(r[m].X)
                for n in range(V_max):
                    for i in range(N):
                        opt_w[m][n][i] = abs(round(w[m,n,i].X,2))
                        for j in range(N):
                            opt_x[m][n][i][j] = round(x[m,n,i,j].X)

            for j in range(N):
                opt_p[j] = round(p[j].X)
                opt_q[j] = round(q[j].X,3)
                opt_t[j] = round(t[j].X,3)

            
            ############### Result File Generation ################
            now = datetime.now() # current date and time
            '''new_folder = 'Results\\'+now.strftime("%d_%m")
            if not os.path.exists(new_folder): os.mkdir(new_folder)
            result_file = new_folder+'\\results_dataset'+file_no+'_'+now.strftime("%m%d_%H%M%S")'''

            ############# Saving the Route Figure ###################
            def node_plot():
                arrow_width = max(max_x,max_y)/30
                y_shift = 0.1*max_x
                x_shift = 0.05*max_x
                veh_arr_flag = [0]*T
                for m in range(T):
                    for n in range(V_max):
                        for i in range(N):
                            for j in range(N):
                                if opt_x[m][n][i][j] ==1: 
                                    # Added Arrows for the route
                                    if m == 0: 
                                        color = 'coral'
                                        Label_text = 'Veh Type 0'
                                    elif m== 1: 
                                        color = 'purple'
                                        Label_text = 'Veh Type 1'
                                    else: 
                                        color = 'olivedrab'
                                        Label_text = 'Veh Type 2'
                                    
                                    arrow = mpl.arrow(X[i],Y[i],X[j]-X[i],Y[j]-Y[i],length_includes_head = True,
                                        head_width=arrow_width,fc=color,ec=color)

                                    if not veh_arr_flag[m]: arrow.set_label(Label_text)
                                    veh_arr_flag[m] = 1

                                    # Add number of units carried on the arrows
                                    mid_x = (X[j]+X[i])/2 +x_shift
                                    mid_y = (Y[j]+Y[i])/2
                                    if j<i and opt_x[m][n][j][i] ==1: mid_y-=y_shift
                                    annotate = mpl.annotate(f'{opt_w[m][n][i]}', (mid_x, mid_y),color='brown')
                        
                            # Added Node number
                            if m == 0: 
                                mpl.annotate(i, (X[i], Y[i]+0.15))
                                if not i==0: mpl.annotate(f'D={D[i]}', (X[i]+x_shift, Y[i]-0.3),color='red')
                          

                mpl.plot(X,Y,'b*')  
                mpl.legend(loc='best')     
                mpl.title('Optimised Route')
                mpl.xlabel('X-coordinate [Km]')
                mpl.ylabel('Y-coordinate [Km]')
                mpl.xlim((-max_x-(0.25*max_x),max_x+(0.25*max_x)))
                mpl.ylim((-max_y-(0.2*max_y),max_y+(0.2*max_y)))
                mpl.savefig(result_file+'_'+now.strftime("%m%d_%H%M%S")+'.png')
                mpl.close()

            node_plot()
            
            ########### Saving results in text file ##########################
            with open(result_file+'_'+now.strftime("%m%d_%H%M%S")+'.txt','w') as res:
                print("------------------- Solution --------------------" ,file=res)
                print('Total # of Nodes:- ', N,file=res)
                v_total = 0
                for m in range(T):
                    v_total += V[m]

                print('Total # of Vehicles:- ',v_total,file=res)
                print('\nTotal # of Variables:- ',model.NumVars,file=res)
                print(f'\tInteger:{model.NumIntVars} (Bin: {model.NumBinVars}) Continuous: {model.NumVars-model.NumIntVars}',file=res)
                print('Total # of Constraints:- ',model.NumConstrs,file=res)
                print(f'Total Solutions Found: {model.SolCount}',file=res)
                print(f'Gap Optimality: {round(gap,2)}',file=res)
                print(f'Time Taken: {round(model.Runtime,2)} sec',file=res)
                if gap > 0.1:
                    print(f'Best Bound: {round(best_z,2)}',file=res)
                print(f"Objective value (Minimum Cost): {opt_Z}",file=res)
                print('\nVariable Values:-',file=res)
                print('\tLate Arrival:',file=res)
                for j in range(N):
                    print(f"\t\tN{j} :-- p[{j}] = {opt_p[j]}",file=res)
                print('\tQuality at Arrival:',file=res)
                for j in range(N):
                    print(f"\t\tN{j} :-- q[{j}] = {opt_q[j]}",file=res)
                print('\tTime Of Arrival:',file=res)
                for j in range(N):
                    print(f"\t\tN{j} :-- t[{j}] = {opt_t[j]} :: L_a[{j}] = {L_a[j]}",file=res)

                print('\tVehicles Used:',file=res)
                for m in range(T):
                    print(f'\t\tV{m} :- r[{m}] = {opt_r[m]} <= {V[m]}',file=res)
                print('\tVehicle Route:',file=res)
                for m in range(T):
                    for n in range(V_max):
                        for i in range(N):
                            for j in range(N):
                                print(f"\t\tV{m}[{n}] N{i}->N{j} :-- x[{m},{n},{i},{j}] = {opt_x[m][n][i][j]}",file=res)
                                

                print('\tProduct Left After Node:',file=res)
                for m in range(T):
                    for n in range(V_max):
                        for j in range(N):
                            print(f"\t\tV{m}[{n}] After N{j} :-- w[{m},{n},{j}] = {opt_w[m][n][j]}",file=res)

            self.CurrObjVal = opt_Z
            self.GapOptimality = gap
            self.BestBound = best_z
            self.VehiclesUsed = opt_r[:]
        else:
            print('!!!!!!!!!!!!!!!!!!!!!!!!\nMODEL IS INFEASIBLE OR UNBOUNDED.')
            self.CurrObjVal = -100
            self.GapOptimality = 100
            self.BestBound = -100
            self.VehiclesUsed = [0]*T

        print('\nProcess Exited.')


        
                