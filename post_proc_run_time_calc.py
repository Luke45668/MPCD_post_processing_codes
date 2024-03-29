##!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script will load in an array of run time data  by reading lammps log files. T
"""
#%%
#NOTE need to turn script bck into functions 
import os
from random import sample
import numpy as np
import matplotlib.pyplot as plt
import regex as re
import pandas as pd
import sigfig
plt.rcParams.update(plt.rcParamsDefault)
#plt.rcParams['text.usetex'] = True
from mpl_toolkits import mplot3d
from matplotlib.gridspec import GridSpec
import scipy.stats
from datetime import *
path_2_post_proc_module= '/Volumes/Backup Plus 1/PhD_/Rouse Model simulations/Using LAMMPS imac/LAMMPS python run and analysis scripts/Analysis codes'
os.chdir(path_2_post_proc_module)
from post_MPCD_MP_processing_module import *
swap_rate = np.array([15]) # values chosen from original mp paper
swap_number = np.array([1])
vel_target=np.array(['INF',10,5,1,0.8,0.6,0.4,0.2,0.1,0.01,0.001]) 

                    

fluid_name='vtargetnubar'
fluid_name='swaprate'
vel_target=np.array([0.8])
swap_rate=np.array([15,30,60,90,120,150,180,360])
##%% # need to use the same set up as reading and organising log files before, then only read the run time 


VP_general_name_string='vel.'+fluid_name+'**'

Mom_general_name_string='mom.'+fluid_name+'**'

log_general_name_string='log.'+fluid_name+'_**'
                         #log.H20_no466188_wall_VACF_output_no_rescale_
TP_general_name_string='temp.'+fluid_name+'**'

dump_general_name_string='test_run_dump_'+fluid_name+'_*'

filepath='pure_fluid_new_method_validations/Final_MPCD_val_run/fluid_visc_0.52_data/swaprate_test'
#filepath='pure_fluid_new_method_validations/Final_MPCD_val_run/fluid_visc_0.52_data/vtarget_test'
#filepath='pure_fluid_new_method_validations/T_1/prod_runs_swap_rate_var'
realisation_name_info= VP_and_momentum_data_realisation_name_grabber(TP_general_name_string,log_general_name_string,VP_general_name_string,Mom_general_name_string,filepath,dump_general_name_string)
realisation_name_Mom=realisation_name_info[0]
realisation_name_VP=realisation_name_info[1]
count_mom=realisation_name_info[2]
count_VP=realisation_name_info[3]
realisation_name_log=realisation_name_info[4]
count_log=realisation_name_info[5]
realisation_name_dump=realisation_name_info[6]
count_dump=realisation_name_info[7]
realisation_name_TP=realisation_name_info[8]
count_TP=realisation_name_info[9]
from datetime import timedelta
def run_time_reader(realisation_name):
   #format_string = "%HH:%MM:SS"
   run_data_start= ("Total wall time: ")
   run_data_start_bytes=bytes(run_data_start,'utf-8')

   with open(realisation_name) as f:
      read_data = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ ) 

      run_data_seek=read_data.find(run_data_start_bytes)  
      read_data.seek(run_data_seek) 

      
      run_time_bytes=read_data.read()
      
      read_data.close()
   run_time=str(run_time_bytes)[18:27].replace(" ", "")

   run_time=run_time.replace( "\\","")
   #run_time=run_time.replace(":","")
   #print(run_time)
   #print(len(run_time))
   epoch_time = datetime(1900, 1, 1)
   #run_time=datetime.strptime( run_time, format_string)
   if len(run_time)==8:
       run_time=timedelta(seconds=int(run_time[6:8]), minutes=int(run_time[3:5]),hours=int(run_time[0:2]) )
   #delta = (run_time - epoch_time)
   else: 
       run_time=timedelta(seconds=int(run_time[5:7]), minutes=int(run_time[2:4]),hours=int(run_time[0]) )
       
   
   run_time=int(run_time.total_seconds())
   
   return run_time
#run_time_reader("log.genericSRD_no922300_wall_pure_output_no_rescale_154590_1_2109375_75.0_0.00698428772378578_10_10000_10000_2000000_T_1_lbda_0.0698428772378578_SR_15_SN_1_VT_1")

##%%log file reader and organiser
fluid_names=fluid_name
log_EF=21
log_SN=23
log_realisation_index=8

loc_fluid_name=0
j_=3
loc_no_SRD=9
no_SRD=[]
box_size=[]
no_SRD=np.zeros((count_log,1),dtype=int)
fluid_name_array=np.zeros((count_log,1),dtype=str)

# not happy with this bit of code, could ceertainly be more elegant 
for i in range(0,count_log):
    filename=realisation_name_log[i].split('_')
    print(filename[loc_no_SRD])
    no_SRD[i,0] = filename[loc_no_SRD]
    print(filename[loc_fluid_name][4:])
    fluid_name_array[i,0] = filename[loc_fluid_name][4:]

no_SRD_and_fluid_names = np.concatenate((fluid_name_array,no_SRD),axis=1)
fluid_name_array=np.unique(no_SRD_and_fluid_names,axis=0)


#%%
    
# no_SRD.sort(key=int)
# no_SRD.sort()
# no_SRD_key=[]

#using list comprehension to remove duplicates
# [no_SRD_key.append(x) for x in no_SRD if x not in no_SRD_key]

Path_2_log='/Volumes/Backup Plus 1/PhD_/Rouse Model simulations/Using LAMMPS imac/MYRIAD_LAMMPS_runs/'+filepath
thermo_vars='         KinEng          Temp          TotEng    '
from log2numpy import * 
total_cols_log=4
#org_var_log_1=vel_target
#loc_org_var_log_1=25
org_var_log_1=swap_rate
loc_org_var_log_1=21
org_var_log_2=swap_number#spring_constant
loc_org_var_log_2=log_SN


def log_run_time_reader(loc_no_SRD,org_var_log_1,loc_org_var_log_1,org_var_log_2,loc_org_var_log_2,j_,count_log,realisation_name_log,log_realisation_index,fluid_names,loc_fluid_name):
    
   
   
   
    run_time_array_with_all_realisations=np.zeros((len(fluid_names),j_,org_var_log_1.size,org_var_log_2.size,))
    run_time_array_unsorted_srd_bins=()
    for i in range(0,fluid_name_array.shape[0]):
        run_time_array_unsorted_srd_bins=run_time_array_unsorted_srd_bins+(run_time_array_with_all_realisations,)
        
        
   

    for i in range(0,count_log):
        filename=realisation_name_log[i].split('_')
        realisation_name_for_run_time=realisation_name_log[i]
        realisation_index=int(float(realisation_name_log[i].split('_')[log_realisation_index]))
        fluid_identifier=filename[loc_fluid_name][4:]
        
        

        if isinstance(fluid_identifier,(str)):
            fluid_name_find_in_selection=fluid_identifier
            fluid_name_index=fluid_names.index(fluid_name_find_in_selection)
        else:
            break
        if isinstance(filename[loc_no_SRD],(int)):
            no_srd_in_selection=filename[loc_no_SRD]
            #no_srd_index=no_SRD_key.index(no_srd_in_selection)
            fluid_name_array_fluid_col_index = np.where(fluid_name_array[:,0]==fluid_names[fluid_name_index][0])
            no_srd_row_index=np.where(int(filename[loc_no_SRD])==fluid_name_array[:,1])
            if no_srd_row_index == fluid_name_array_fluid_col_index :
                
                fluid_name_no_srd_tuple_index = no_srd_row_index
                print(fluid_name_no_srd_tuple_index)
                
            else:
                break 
        else:
            break
        if isinstance(filename[loc_org_var_log_1],int):
            org_var_log_1_find_in_name=int(filename[loc_org_var_log_1])
            org_var_1_index=np.where(org_var_log_1==org_var_log_1_find_in_name)[0][0]
        else:
            org_var_log_1_find_in_name=float(filename[loc_org_var_log_1])
            org_var_1_index=np.where(org_var_log_1==org_var_log_1_find_in_name)[0][0]
        
        if isinstance(filename[loc_org_var_log_2],int):
            org_var_log_2_find_in_name=int(filename[loc_org_var_log_2])
            org_var_2_index= np.where(org_var_log_2==org_var_log_2_find_in_name)[0][0] 
        else:
            org_var_log_2_find_in_name=float(filename[loc_org_var_log_2])
            org_var_2_index= np.where(org_var_log_2==org_var_log_2_find_in_name)[0][0] 
            
        # multiple swap numbers and swap rates
        #log_file_tuple[np.where(swap_rate==swap_rate_org)[0][0]][np.where(swap_number==swap_number_org)[0][0],realisation_index,:,:]=log2numpy_reader(realisation_name_log[i],Path_2_log,thermo_vars)
    
        run_time_array_unsorted_srd_bins[fluid_name_no_srd_tuple_index][fluid_name_index,realisation_index,org_var_1_index, org_var_2_index]=run_time_reader(realisation_name_for_run_time) # need a new function that simply grabs the run time from end of the file 
    
    return run_time_array_unsorted_srd_bins
    


##%%
run_time_array_with_all_realisations=np.zeros((fluid_name_array.shape[0],j_,org_var_log_1.size,org_var_log_2.size,))
run_time_array_unsorted_srd_bins=()

for i in range(0,fluid_name_array.shape[0]):
    run_time_array_unsorted_srd_bins=run_time_array_unsorted_srd_bins+(run_time_array_with_all_realisations,)
    
 

#for i in range(0,count_log):
#for i in range(0,120):
#for i in range(120,125):    
for i in range(0,count_log): 
    filename=realisation_name_log[i].split('_')
    realisation_name_for_run_time=realisation_name_log[i]
    #print(realisation_name_for_run_time)
    realisation_index=int(float(realisation_name_log[i].split('_')[log_realisation_index]))-1
    
    fluid_identifier=filename[loc_fluid_name][4:]
    #print("fluid_identifier",fluid_identifier)
    fluid_name_index=fluid_names.index(fluid_identifier)
    #print("fluid_name_index", fluid_name_index)
    #print(filename[loc_no_SRD])
    fluid_name_array_fluid_col_index = np.where(fluid_name_array[:,0]==fluid_names[fluid_name_index][0])
    #print("fluid_name_array_fluid_col_index",fluid_name_array_fluid_col_index)
    no_srd_row_index=np.where(filename[loc_no_SRD]==fluid_name_array[:,1])[0]
    #print("no_srd_row_index",no_srd_row_index)
    a = no_srd_row_index[:]
    b =fluid_name_array_fluid_col_index[0].flatten()
    name_number_comparison = [np.where(a==x) for x in b]
    correct_fluid_index=[]
    for j in range(0,len(name_number_comparison)):
        if name_number_comparison[j][0].size == 0:
           continue 
        elif name_number_comparison[j][0] == 0:
            correct_fluid_index.append(j)
        elif name_number_comparison[j][0] == 1:
            correct_fluid_index.append(j)
        else: 
            print("SRD and fluid name not matched")
            break 
    #print("correct_fluid_index",correct_fluid_index)
    
    #print(fluid_name_no_srd_tuple_index)
    if isinstance(filename[loc_org_var_log_1],int):
        org_var_log_1_find_in_name=int(filename[loc_org_var_log_1])
        org_var_1_index=np.where(org_var_log_1==org_var_log_1_find_in_name)[0][0]
    # if there is a string variable input 
    # switch on for vel target tests
    # elif isinstance(filename[loc_org_var_log_1],str):
    #     org_var_log_1_find_in_name=(filename[loc_org_var_log_1])
    #     org_var_1_index=np.where(org_var_log_1==org_var_log_1_find_in_name)[0][0]

    else:
        org_var_log_1_find_in_name=float(filename[loc_org_var_log_1])
        org_var_1_index=np.where(org_var_log_1==org_var_log_1_find_in_name)[0][0]
    
    if isinstance(filename[loc_org_var_log_2],int):
        org_var_log_2_find_in_name=int(filename[loc_org_var_log_2])
        org_var_2_index= np.where(org_var_log_2==org_var_log_2_find_in_name)[0][0] 
    else:
        org_var_log_2_find_in_name=float(filename[loc_org_var_log_2])
        org_var_2_index= np.where(org_var_log_2==org_var_log_2_find_in_name)[0][0] 
        
    # multiple swap numbers and swap rates
    #log_file_tuple[np.where(swap_rate==swap_rate_org)[0][0]][np.where(swap_number==swap_number_org)[0][0],realisation_index,:,:]=log2numpy_reader(realisation_name_log[i],Path_2_log,thermo_vars)
    #print(fluid_name_no_srd_tuple_index[0])
    # print(realisation_index)
    # print(org_var_1_index) 
    # print(org_var_2_index)
    # print(run_time_reader(realisation_name_for_run_time))
    fluid_name_no_srd_index =fluid_name_array_fluid_col_index[0][correct_fluid_index]
    #print( fluid_name_no_srd_index)
    
    run_time_array_with_all_realisations[fluid_name_no_srd_index,realisation_index,org_var_1_index, org_var_2_index]=run_time_reader(realisation_name_for_run_time)
    #print( run_time_array_unsorted_srd_bins[fluid_name_no_srd_tuple_index[0]])
# %%
plt.rcParams['text.usetex'] = True

# run time vs swap rate
#NOTE: need to consider this averaging 
#NOTE: need to consider how exactly to plot, could be a quad plot with one set of data for each swap rate

run_time_array_with_all_realisations_real_av=np.mean(run_time_array_with_all_realisations,axis=1)
run_time_array_with_all_realisations_swap_av=np.mean(run_time_array_with_all_realisations_real_av,axis=1)
run_time_array_with_all_realisations_swap_num_av=np.mean(run_time_array_with_all_realisations_swap_av,axis=1)



def func4(x, a, b):
   #return np.log(a) + np.log(b*x)
   #return (a*(x**b))
   #return 10**(a*np.log(x) + b)
   return (a*x) +b 
   #return np.log(a*x) +b

# run time vs SRD count 
plt.rcParams.update({'font.size': 15})
fluid_names_=fluid_name  # are the labels correct
linestyle=["--","-",":","-."]
marker=["x","o","+","^"]
swap_number_index=3
no_srd_values= np.asarray(fluid_name_array[:,1] , dtype=float)
#no_srd_values=np.flip(np.reshape(no_srd_values,(4,3)),axis=1)
#run_time_array_with_all_realisations_swap_av=np.flip(np.reshape(run_time_array_with_all_realisations_swap_av[:,swap_number_index],(4,3)),axis=1)
# for i in range(0,2):
#     run_time_array_with_all_realisations_swap_av_vstack=np.concatenate(run_time_array_with_all_realisations_swap_av[:,i],run_time_array_with_all_realisations_swap_av[:,i+1])
# fitting_params=()
# for i in range(0,4):
#     fitting_params= fitting_params+(scipy.optimize.curve_fit(func4,no_srd_values[i,:],run_time_array_with_all_realisations_swap_av[i,:],method='lm',maxfev=5000)[0],)
#     #fitting_params= fitting_params+(np.polyfit(no_srd_values[i,:],run_time_array_with_all_realisations_swap_av[i,:],3),)
   
# run_time_array_with_all_realisations_swap_av_for_plot=np.concatenate((run_time_array_with_all_realisations_swap_av[:,0],run_time_array_with_all_realisations_swap_av[:,1],run_time_array_with_all_realisations_swap_av[:,2]),axis=0)
# no_srd_values=np.concatenate((no_srd_values[:,0],no_srd_values[:,1],no_srd_values[:,2]),axis=0)

# plotting_data=np.array([no_srd_values,run_time_array_with_all_realisations_swap_av_for_plot])

# print(plotting_data[0,:]==no_srd_values)
# print(plotting_data[1,:]==run_time_array_with_all_realisations_swap_av_for_plot)

# plotting_data=plotting_data[:,plotting_data[0,:].argsort()]

# print(plotting_data[0,:]==no_srd_values)
# print(plotting_data[1,:]==run_time_array_with_all_realisations_swap_av_for_plot)


# fitting_params=scipy.optimize.curve_fit(func4,no_srd_values,run_time_array_with_all_realisations_swap_av_for_plot,method='lm',maxfev=5000)[0]
# y_residuals= func4(no_srd_values[:],fitting_params[0],fitting_params[1])-run_time_array_with_all_realisations_swap_av_for_plot
# std_error_in_fit= np.sqrt(np.mean(y_residuals**2)) 


def func4(x, a, b):
   #return np.log(a) + np.log(b*x)
   #return (a*(x**b))
   #return 10**(a*np.log(x) + b)
   return (a*x) +b 
#%%
# vel swap 
fitting_params=np.zeros((fluid_name_array.shape[0],3))

#for z in range(fluid_name_array.shape[0]):
for z in range(vel_target.size):
    # vel swap data 
    #fitting=scipy.stats.linregress(no_srd_values[:],run_time_array_with_all_realisations_real_av[:,z,0])
    # swap rate 
    fitting=scipy.stats.linregress(no_srd_values[:],run_time_array_with_all_realisations_real_av[:,z,0])
    fitting_params[z,0]=fitting.slope
    fitting_params[z,1]=fitting.intercept
    fitting_params[z,2]=fitting.stderr

fitting_params=np.mean(fitting_params, axis=0)
#%% swap rater
fitting_params=np.zeros((swap_rate.size,3))

#for z in range(fluid_name_array.shape[0]):
for z in range(swap_rate.size):
    # vel swap data 
    #fitting=scipy.stats.linregress(no_srd_values[:],run_time_array_with_all_realisations_real_av[:,z,0])
    # swap rate 
    fitting=scipy.stats.linregress(no_srd_values[:],run_time_array_with_all_realisations_real_av[:,z,0])
    fitting_params[z,0]=fitting.slope
    fitting_params[z,1]=fitting.intercept
    fitting_params[z,2]=fitting.stderr

fitting_params=np.mean(fitting_params, axis=0)


#%% vel swap version 
colour = [
 'black',
 'blueviolet',
 'cadetblue',
 'chartreuse',
 'coral',
 'cornflowerblue',
 'crimson',
 'cyan',
 'darkblue',
 'darkcyan',
 'darkgoldenrod',
 'darkgray']

plt.rcParams.update({'font.size': 25})
fontsize=35
labelpadx=15
labelpady=35
#print(run_time_array_with_all_realisations_swap_av_for_plot[:])
#print(no_srd_values[:])
marker=['x','o','+','^',"1","X","d","*","P","v","."]
width_plot=8
height_plot=6
#%y_error_bar=np.abs(np.exp(shear_rate_mean_error_of_both_cells[:,:,0]))
os.getcwd()
plt.figure(figsize=(width_plot,height_plot))  
for z in range(0,fluid_name_array.shape[0]):
    plt.scatter(no_srd_values[:],run_time_array_with_all_realisations_real_av[:,z,0],label="$v_{target}="+str(vel_target[z])+"$", marker=marker[z],color=colour[z])
   # plt.scatter(no_srd_values[:],run_time_array_with_all_realisations_real_av[:,z,0],label="$f_{p}="+str(swap_rate[z])+"$", marker=marker[z],color=colour[z])
   
    plt.xlabel("$N_{SRD}[-]$", labelpad=labelpadx)
    plt.ylabel("$t_{\infty}[s]$", rotation=0,labelpad=labelpady)
    #plt.legend(loc="best",  bbox_to_anchor=(1.05, 1.3) )
    #plt.savefig("All_fluids_run_time_vs_particle_count_swap_number_"+str(swap_number[swap_number_index])+".pdf",dpi=500,bbox_inches='tight' )
plt.plot(no_srd_values[:],func4(no_srd_values[:],fitting_params[0],fitting_params[1]))
plt.legend(loc="best",  bbox_to_anchor=(1, 1.1) )
plt.text(0,-40000,"$y="+str(sigfig.round(fitting_params[0],sigfigs=3))+"x"+str(sigfig.round(fitting_params[1],sigfigs=3))+"$, $\sigma_{M}=\pm"+str(sigfig.round(fitting_params[2],sigfigs=3))+"s$")
plt.savefig("plots/"+fluid_name+"_run_time_data_vs_nsrd_var_vel_target.pdf",dpi=500,bbox_inches='tight' )
plt.show()



#%% swap rate  version 
colour = [
 'black',
 'blueviolet',
 'cadetblue',
 'chartreuse',
 'coral',
 'cornflowerblue',
 'crimson',
 'darkblue',
 'darkcyan',
 'darkgoldenrod',
 'darkgray']

plt.rcParams.update({'font.size': 25})
fontsize=35
labelpadx=15
labelpady=35
#print(run_time_array_with_all_realisations_swap_av_for_plot[:])
#print(no_srd_values[:])
marker=['x','o','+','^',"1","X","d","*","P","v"]
width_plot=8
height_plot=6
#%y_error_bar=np.abs(np.exp(shear_rate_mean_error_of_both_cells[:,:,0]))
os.getcwd()
plt.figure(figsize=(width_plot,height_plot))  
for z in range(0,swap_rate.size):
   # plt.scatter(no_srd_values[:],run_time_array_with_all_realisations_real_av[:,z,0],label="$v_{target}="+str(vel_target[z])+"$", marker=marker[z],color=colour[z])
    plt.scatter(no_srd_values[:],run_time_array_with_all_realisations_real_av[:,z,0],label="$f_{p}="+str(swap_rate[z])+"$", marker=marker[z],color=colour[z])
   
    plt.xlabel("$N_{SRD}[-]$", labelpad=labelpadx)
    plt.ylabel("$t_{\infty}[s]$", rotation=0,labelpad=labelpady)
    #plt.legend(loc="best",  bbox_to_anchor=(1.05, 1.3) )
    #plt.savefig("All_fluids_run_time_vs_particle_count_swap_number_"+str(swap_number[swap_number_index])+".pdf",dpi=500,bbox_inches='tight' )
plt.plot(no_srd_values[:],func4(no_srd_values[:],fitting_params[0],fitting_params[1]))
plt.legend(loc="best",  bbox_to_anchor=(1, 1) )
plt.text(0,-40000,"$y="+str(sigfig.round(fitting_params[0],sigfigs=3))+"x"+str(sigfig.round(fitting_params[1],sigfigs=3))+"$, $\sigma_{M}=\pm"+str(sigfig.round(fitting_params[2],sigfigs=3))+"s$")
plt.savefig("plots/"+fluid_name+"_run_time_data_vs_nsrd_var_swap_rate.pdf",dpi=500,bbox_inches='tight' )
plt.show()


# %%
