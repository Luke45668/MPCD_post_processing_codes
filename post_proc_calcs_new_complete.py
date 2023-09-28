##!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script will given the correct set of input data produce all the plots and velocity profile data 

after an MPCD simulation. 
"""
#%%
#from imp import reload
import os
from random import sample

#from sys import exception
#from tkinter import HORIZONTAL
import numpy as np
#import sklearn as sk
import matplotlib.pyplot as plt
import regex as re
import pandas as pd
#import pyswarms as ps
import sigfig
plt.rcParams.update(plt.rcParamsDefault)
#plt.rcParams['text.usetex'] = True
from mpl_toolkits import mplot3d
from matplotlib.gridspec import GridSpec
#import seaborn as sns

import scipy.stats
from datetime import datetime


path_2_post_proc_module= '/Volumes/Backup Plus 1/PhD_/Rouse Model simulations/Using LAMMPS imac/LAMMPS python run and analysis scripts/Analysis codes'
os.chdir(path_2_post_proc_module)
#import them in the order they should be used 
from mom2numpy import *
from velP2numpy import *
from dump2numpy import * 
import glob 
from post_MPCD_MP_processing_module import *
#importlib.reload(post_MPCD_MP_processing_module)

# define key inputs 
j_=3

swap_rate=np.array([15,30,60,120,240,480,600])
swap_number=np.array([1])
fluid_name='genericSRD'
equilibration_timesteps=1000
VP_ave_freq =10000
chunk = 20
dump_freq=10000 # if you change the timestep rememebr to chaneg this 
thermo_freq = 10000
scaled_temp=1
scaled_timestep=0.01
realisation=np.array([1,2,3])
VP_output_col_count = 4 
r_particle =25e-6 # for some solutions, rememebrr to check if its 25 or 10
phi=0.0577777778
N=2
Vol_box_at_specified_phi=(N* (4/3)*np.pi*r_particle**3 )/phi
box_side_length=np.cbrt(Vol_box_at_specified_phi)
fluid_name='genericSRD'
run_number=''
batchcode='966397'
no_timesteps=3000000 # rememebr to change this depending on run 

# grabbing file names 

VP_general_name_string='vel.'+fluid_name+'*_VACF_output_*_no_rescale_*'

Mom_general_name_string='mom.'+fluid_name+'*_VACF_out_*_no_rescale_*'

log_general_name_string='log.'+fluid_name+'_*_wall_pure_output_no_rescale_*'
                         #log.H20_no466188_wall_VACF_output_no_rescale_
TP_general_name_string='temp.'+fluid_name+'*_VACF_output_*_no_rescale_*'

dump_general_name_string='test_run_dump_'+fluid_name+'_*'




#filepath='VACF_temp_profile_tests/run_'+batchcode
filepath='pure_fluid_new_method_validations/T_1/production_runs'
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
box_size_loc=9
filename_for_lengthscale=realisation_name_VP[0].split('_')
lengthscale=box_side_length/float(filename_for_lengthscale[box_size_loc])


#checking the number of different solutions used in the run
# # locations of key info when string name is split by undescores

loc_no_SRD=8
loc_EF=20
loc_SN=22
loc_Realisation_index= 7
loc_box_size=9

# 
no_SRD=[]
box_size=[]
for i in range(0,count_VP):
    no_srd=realisation_name_VP[i].split('_')
    no_SRD.append(no_srd[loc_no_SRD])
    box_size.append(no_srd[loc_box_size])
    
no_SRD.sort(key=int)
no_SRD.sort()
box_size.sort()
no_SRD_key=[]
box_size_key=[]
#using list comprehension to remove duplicates
[no_SRD_key.append(x) for x in no_SRD if x not in no_SRD_key]
[box_size_key.append(x) for x in box_size if x not in box_size_key]
box_side_length_scaled=[]
for item in box_size_key:
    box_side_length_scaled.append(float(item))
box_side_length_scaled=np.array([box_side_length_scaled])

number_of_solutions=len(no_SRD_key)

simulation_file="MYRIAD_LAMMPS_runs/"+filepath



Path_2_VP="/Volumes/Backup Plus 1/PhD_/Rouse Model simulations/Using LAMMPS imac/"+simulation_file
# new more general version of VP organiser and reader
#reading in velocity profiles, avoid if possible
org_var_1=swap_rate
loc_org_var_1=20
org_var_2=swap_number #spring_constant
loc_org_var_2=22#25
#VP_raw_data= VP_organiser_and_reader(loc_no_SRD,loc_EF,loc_SN,loc_Realisation_index,box_side_length_scaled,j_,number_of_solutions,swap_number,swap_rate,no_SRD_key,realisation_name_VP,Path_2_VP,chunk,equilibration_timesteps,VP_ave_freq,no_timesteps,VP_output_col_count,count_VP)
#%% Velocity profiles 

VP_raw_data=VP_organiser_and_reader(loc_no_SRD,loc_org_var_1,loc_org_var_2,loc_Realisation_index,box_side_length_scaled,j_,number_of_solutions,org_var_1,org_var_2,no_SRD_key,realisation_name_VP,Path_2_VP,chunk,equilibration_timesteps,VP_ave_freq,no_timesteps,VP_output_col_count,count_VP)

VP_data_upper=VP_raw_data[0]
VP_data_lower=VP_raw_data[1]
error_count=VP_raw_data[2]
filename=VP_raw_data[3]
VP_z_data_upper=VP_raw_data[4]
VP_z_data_lower=VP_raw_data[5]

if error_count != 0: 
    print('Error reading velocity profiles, check data !')
else:
    print('Velocity profile data success')


# box_size_loc=9
# lengthscale=box_side_length/float(filename[box_size_loc])
# Temperature profiles
# as long as the VP data have the same structure as the TP data this will work 
TP_raw_data=VP_organiser_and_reader(loc_no_SRD,loc_org_var_1,loc_org_var_2,loc_Realisation_index,box_side_length_scaled,j_,number_of_solutions,org_var_1,org_var_2,no_SRD_key,realisation_name_TP,Path_2_VP,chunk,equilibration_timesteps,VP_ave_freq,no_timesteps,VP_output_col_count,count_VP)

TP_data_upper=TP_raw_data[0]
TP_data_lower=TP_raw_data[1]
error_count=TP_raw_data[2]
filename=TP_raw_data[3]
TP_z_data_upper=TP_raw_data[4]
TP_z_data_lower=TP_raw_data[5]

if error_count != 0: 
    print('Error reading temp profiles, check data !')
else:
    print('Temp profile data success')
    

#%%log file reader and organiser
log_EF=21
log_SN=23
log_K=27
log_realisation_index=8
#def log_file_reader_and_organiser(count_log,):
log_file_col_count=4
log_file_row_count=((no_timesteps)/thermo_freq) +2 # to fit full log file  not sure on it 
log_file_tuple=()
Path_2_log='/Volumes/Backup Plus 1/PhD_/Rouse Model simulations/Using LAMMPS imac/MYRIAD_LAMMPS_runs/'+filepath
#thermo_vars='         KinEng          Temp          TotEng       c_vacf[4]   '
thermo_vars='         KinEng          Temp          TotEng    '
from log2numpy import * 
total_cols_log=4
org_var_log_1=swap_rate
loc_org_var_log_1=log_EF
org_var_log_2=swap_number#spring_constant
loc_org_var_log_2=log_SN

def log_file_organiser_and_reader(org_var_log_1,loc_org_var_log_1,org_var_log_2,loc_org_var_log_2,j_,log_file_row_count,log_file_col_count,count_log,realisation_name_log,log_realisation_index,Path_2_log,thermo_vars):
    
    log_file_tuple=()
    from log2numpy import log2numpy_reader
    for i in range(0,org_var_log_1.size):
        log_4d_array_with_all_realisations=np.zeros((org_var_log_2.size,j_,int(log_file_row_count),log_file_col_count))
        log_file_tuple=log_file_tuple+(log_4d_array_with_all_realisations,)
        
    averaged_log_file=np.zeros((org_var_log_1.size,org_var_log_2.size,int(log_file_row_count),total_cols_log))

    for i in range(0,count_log):
        filename=realisation_name_log[i].split('_')
        realisation_index=int(float(realisation_name_log[i].split('_')[log_realisation_index]))
        print(realisation_index)
        if isinstance(filename[loc_org_var_log_1],int):
            org_var_log_1_find_in_name=int(filename[loc_org_var_log_1])
            tuple_index=np.where(org_var_log_1==org_var_log_1_find_in_name)[0][0]
        else:
            org_var_log_1_find_in_name=float(filename[loc_org_var_log_1])
            tuple_index=np.where(org_var_log_1==org_var_log_1_find_in_name)[0][0]
        
        if isinstance(filename[loc_org_var_log_2],int):
            org_var_log_2_find_in_name=int(filename[loc_org_var_log_2])
            array_index_1= np.where(org_var_log_2==org_var_log_2_find_in_name)[0][0] 
        else:
            org_var_log_2_find_in_name=float(filename[loc_org_var_log_2])
            array_index_1= np.where(org_var_log_2==org_var_log_2_find_in_name)[0][0] 
            
        # multiple swap numbers and swap rates
        #log_file_tuple[np.where(swap_rate==swap_rate_org)[0][0]][np.where(swap_number==swap_number_org)[0][0],realisation_index,:,:]=log2numpy_reader(realisation_name_log[i],Path_2_log,thermo_vars)
        log_file_tuple[tuple_index][array_index_1,realisation_index,:,:]=log2numpy_reader(realisation_name_log[i],Path_2_log,thermo_vars)


    for k in range(0,org_var_log_1.size):
        for i in range(0,org_var_log_2.size):
            print(np.mean(log_file_tuple[k][i],axis=0).shape)
            averaged_log_file[k,i,:,:]=np.mean(log_file_tuple[k][i],axis=0)
    
    return  averaged_log_file
    

averaged_log_file=log_file_organiser_and_reader(org_var_log_1,loc_org_var_log_1,org_var_log_2,loc_org_var_log_2,j_,log_file_row_count,log_file_col_count,count_log,realisation_name_log,log_realisation_index,Path_2_log,thermo_vars)
time_vector_from_timestep= (averaged_log_file[0,0,:,0] -equilibration_timesteps )* scaled_timestep

#%% plotting E vs Nt and T vs Nt
# legend colours still dont match 
fontsize=15
labelpad=20
#plotting temp vs time 
temp=1
legendx=1.4
# T vs time 
for k in range(0,org_var_1.size):
    for i in range(org_var_2.size):
        
        plt.plot(averaged_log_file[k,i,:,0],averaged_log_file[k,i,:,2],label='$f_p=${}'.format(org_var_1[k]))
    
        x=np.repeat(temp,averaged_log_file[k,i,:,0].shape[0])
        #plt.plot(averaged_log_file[k,i,:,0],x[:],label='$f_v=${}'.format(org_var_2[i]))
       # plt.plot(averaged_log_file[k,i,:,0],x[:],label='$K=${}'.format(org_var_2[i]))
        plt.xlabel('$N_{t}[-]$',fontsize=fontsize)
        plt.ylabel('$T[\\frac{T k_{B}}{\\varepsilon}]$', rotation=0,fontsize=fontsize,labelpad=labelpad)
       # plt.title(fluid_name+" simulation run $\phi=$"+str(phi)+",All $f_{v_{x}}=$, $N_{v,x}=$"+str(org_var_1[k])+", $\\bar{T}="+str(scaled_temp)+"$, $\ell="+str(lengthscale)+"$")
        #plt.title(fluid_name+" simulation run $\phi=$"+str(phi)+", All K, $f_{v,x}=$"+str(org_var_1[k])+", $\\bar{T}="+str(scaled_temp)+"$, $\ell="+str(lengthscale)+"$")
        plt.legend(loc=7,bbox_to_anchor=(legendx, 0.5))
plt.show()
for k in range(0,org_var_1.size):
    #plotting energy vs time 
    for i in range(org_var_2.size):
        #plotting energy vs time 
        #plt.plot(averaged_log_file[k,i,:,0],averaged_log_file[k,i,:,3],label='$f_v=${}'.format(org_var_2[i]))
        plt.plot(averaged_log_file[k,i,:,0],averaged_log_file[k,i,:,3],label='$f_p=${}'.format(org_var_1[k]))
        plt.xlabel('$N_{t}[-]$',fontsize=fontsize)
        plt.ylabel('$E_{t}[\\frac{\\tau^{2}}{\mu \ell^{2}}]$', rotation=0,fontsize=fontsize,labelpad=labelpad)
       # plt.title(fluid_name+" simulation run $\phi=$"+str(phi)+",All $f_{v_{x}}=$, $N_{v,x}=$"+str(org_var_1[k])+", $\\bar{T}="+str(scaled_temp)+"$, $\ell="+str(lengthscale)+"$")
        #plt.title(fluid_name+" simulation run $\phi=$"+str(phi)+", All $K$, $f_{v,x}=$"+str(org_var_1[k])+", $\\bar{T}="+str(scaled_temp)+"$, $\ell="+str(lengthscale)+"$")
        
        plt.legend(loc=7,bbox_to_anchor=(legendx, 0.5))
plt.show()
#%%VACF plot
#averaged_log_file_VACF=averaged_log_file[:,:,:300,4]
# plt.rcParams.update({
#     "text.usetex": True,
#     "font.family": "Helvetica"
# })
plt.rcParams.update({'font.size': 25})
VACF_cut_off=200
fontsize=20
labelpadx=15
labelpady=50
labelpad=50
width_plot=15
height_plot=10
legendx=1
legend_y_pos=1
def func4(x, a, b):
   return a * np.exp(b*x)

VACF_fitting_params=()
VACF_covariance_time=()
VACF_std_error=()
VACF_fitting_params_time=()
VACF_infodict_out =()
for k in range(0,org_var_1.size):    
    for i in range(0,org_var_2.size):
      
        #VACF_fitting_params= VACF_fitting_params+(scipy.optimize.curve_fit(func4,averaged_log_file[k,i,:VACF_cut_off,0],averaged_log_file[k,i,:VACF_cut_off,4],method='lm',maxfev=5000)[0],)
        VACF_fitting_params= VACF_fitting_params+(scipy.optimize.curve_fit(func4,averaged_log_file[k,i,:VACF_cut_off,0],averaged_log_file[k,i,:VACF_cut_off,4],p0=[0, 0], bounds=(-np.inf, np.inf))[0],)
       
       
sample_rate=25

for k in range(0,org_var_1.size):
    for i in range(org_var_2.size):
        
        plt.scatter(averaged_log_file[k,i,:VACF_cut_off:sample_rate,0],averaged_log_file[k,i,:VACF_cut_off:sample_rate,4],label='$f_p=${}'.format(org_var_1[k]))
        plt.plot(averaged_log_file[k,i,:VACF_cut_off:sample_rate,0],func4(averaged_log_file[k,i,:VACF_cut_off:sample_rate,0],VACF_fitting_params[k][0],VACF_fitting_params[k][1]))
        plt.xlabel('$N_{t}[-]$',fontsize=fontsize)
        plt.ylabel('$C_{\\nu}(N_{c}\Delta t)$', rotation=0,fontsize=fontsize,labelpad=labelpad)
       
        plt.legend(loc=7,bbox_to_anchor=(1.55, 0.5))
        print(VACF_fitting_params)
plt.savefig(fluid_name+"_All_swaps_VACF_sample_rate_"+str(sample_rate)+"_cut_off_"+str(VACF_cut_off)+"_batch_"+str(batchcode)+".pdf",dpi=500, bbox_inches='tight')
plt.show()


for k in range(0,org_var_1.size):    
    for i in range(0,org_var_2.size):
        VACF_fit_calc=scipy.optimize.curve_fit(func4,time_vector_from_timestep[:VACF_cut_off:sample_rate],averaged_log_file[k,i,:VACF_cut_off:sample_rate,4],p0=[0, 0], bounds=(-np.inf, np.inf),full_output=True)
        #VACF_fitting_params= VACF_fitting_params+(scipy.optimize.curve_fit(func4,averaged_log_file[k,i,:VACF_cut_off,0],averaged_log_file[k,i,:VACF_cut_off,4],method='lm',maxfev=5000)[0],)
        VACF_fitting_params_time= VACF_fitting_params_time+ (VACF_fit_calc[0],)
        VACF_covariance_time = VACF_covariance_time +(VACF_fit_calc[1],)
    
       

number_of_data_points= VACF_cut_off/sample_rate
standard_error_fit= ()

for k in range(0,1):
    for i in range(org_var_2.size):
        
        standard_error_fit=standard_error_fit + (np.sqrt(np.mean(((func4(time_vector_from_timestep[:VACF_cut_off:sample_rate],VACF_fitting_params_time[k][0],VACF_fitting_params_time[k][1])- averaged_log_file[k,i,:VACF_cut_off:sample_rate,4])**2)/number_of_data_points)),) 
        plt.scatter(time_vector_from_timestep[:VACF_cut_off:sample_rate],averaged_log_file[k,i,:VACF_cut_off:sample_rate,4],marker='x')#,label='$f_p=${}'.format(org_var_1[k]))
        plt.plot(time_vector_from_timestep[:VACF_cut_off:sample_rate],func4(time_vector_from_timestep[:VACF_cut_off:sample_rate],VACF_fitting_params_time[k][0],VACF_fitting_params_time[k][1]),'--',label= "$y=ae^{bx}$, $a=$"+str(sigfig.round(VACF_fitting_params_time[k][0],sigfigs=4))+" and $b=$"+str(sigfig.round(VACF_fitting_params_time[k][1],sigfigs=4))+", $\sigma_{m}=$"+str(sigfig.round(standard_error_fit[k],sigfigs=4)))
        plt.xlabel('$t/\\tau$')
        plt.ylabel('$C_{\\nu}(N_{c}\Delta t)$', rotation=0,labelpad=labelpad)
      
        plt.legend(loc=7,bbox_to_anchor=(1.3, -0.35))
        print(VACF_fitting_params)
plt.savefig(fluid_name+"_VACF_sample_rate_"+str(sample_rate)+"_cut_off_"+str(VACF_cut_off)+"_batch_"+str(batchcode)+".pdf",dpi=500, bbox_inches='tight')
plt.show()
#%% VACF integral for diffusivity for unormalised VACF
degrees_of_freedom = 3
#play with cut off till the integral value remains approximately constant
VACF_cut_off=300
fontsize=20
labelpadx=15
labelpady=50
labelpad=50
width_plot=15
height_plot=10
legendx=1
legend_y_pos=1
sample_rate=1


for k in range(0,1):
    for i in range(org_var_2.size):
       
        plt.plot(time_vector_from_timestep[:VACF_cut_off:sample_rate],averaged_log_file[k,i,:VACF_cut_off:sample_rate,4],marker='x')#,label='$f_p=${}'.format(org_var_1[k]))
        plt.xlabel('$t/\\tau$')
        plt.ylabel('$C_{\\nu}(N_{c}\Delta t)$', rotation=0,labelpad=labelpad)
      
        plt.legend(loc=7,bbox_to_anchor=(1.3, -0.35))
        
#plt.savefig(fluid_name+"_All_swaps_VACF_sample_rate_"+str(sample_rate)+"_cut_off_"+str(VACF_cut_off)+"_batch_"+str(batchcode)+".pdf",dpi=500, bbox_inches='tight')
plt.show()

diffusivity= np.trapz(averaged_log_file[k,i,:VACF_cut_off:sample_rate,4],time_vector_from_timestep[:VACF_cut_off:sample_rate], dx=0.0001,axis=0)/degrees_of_freedom
print(diffusivity)




#%% reading in mom files (much faster)
#  obtaining the mom data size
#Path_2_mom_file="/Volumes/Backup Plus 1/PhD_/Rouse Model simulations/Using LAMMPS imac/"+simulation_file
Path_2_mom_file=Path_2_VP
org_var_mom_1=swap_rate
loc_org_var_mom_1=20
org_var_mom_2=swap_number #spring_constant 
loc_org_var_mom_2=22#25
mom_data_pre_process= mom_file_data_size_reader(j_,number_of_solutions,count_mom,realisation_name_Mom,no_SRD_key,org_var_mom_1,org_var_mom_2,Path_2_mom_file)
size_array=mom_data_pre_process[0]
mom_data= mom_data_pre_process[1]
pass_count= mom_data_pre_process[2]

if pass_count!=count_VP:
    print("Data import error, number of momentum files should match number of velocity files" )
else:
    print("Data size assessment success!")

# Reading in mom data files 
mom_data_files=Mom_organiser_and_reader(mom_data,count_mom,realisation_name_Mom,no_SRD_key,org_var_mom_1,loc_org_var_mom_1,org_var_mom_2,loc_org_var_mom_2,Path_2_mom_file)

mom_data=mom_data_files[0]
error_count_mom=mom_data_files[1]
failed_list_realisations=[2]

if error_count_mom !=0:
    print("Mom file error, check data files aren't damaged")
else:
    print("Mom data import success")


# Now assess the steady state of the VP data 
org_var_1=swap_rate
org_var_2=swap_number#spring_constant 
VP_shear_rate_and_stat_data=VP_data_averaging_and_stat_test_data(VP_z_data_upper,VP_z_data_lower,no_timesteps,VP_data_lower,VP_data_upper,number_of_solutions,org_var_1,org_var_2,VP_ave_freq)
pearson_coeff_upper=VP_shear_rate_and_stat_data[0]
shear_rate_upper=VP_shear_rate_and_stat_data[1]
pearson_coeff_lower=VP_shear_rate_and_stat_data[2]
shear_rate_lower=VP_shear_rate_and_stat_data[3]
timestep_points=VP_shear_rate_and_stat_data[4]
VP_data_lower_realisation_averaged=VP_shear_rate_and_stat_data[5]
VP_data_upper_realisation_averaged=VP_shear_rate_and_stat_data[6]
shear_rate_upper_error=VP_shear_rate_and_stat_data[7]
shear_rate_lower_error=VP_shear_rate_and_stat_data[8]
# TP data
org_var_1=swap_rate
org_var_2=swap_number

TP_shear_rate_and_stat_data=VP_data_averaging_and_stat_test_data(TP_z_data_upper,TP_z_data_lower,no_timesteps,TP_data_lower,TP_data_upper,number_of_solutions,org_var_1,org_var_2,VP_ave_freq)

TP_data_lower_realisation_averaged=TP_shear_rate_and_stat_data[5]
TP_data_upper_realisation_averaged=TP_shear_rate_and_stat_data[6]


#%%

plt.rcParams.update({'font.size': 15})   
import sigfig
lengthscale= sigfig.round(lengthscale,sigfigs=3)
box_size_nd= box_side_length_scaled 
# get rid of this on laptop or code will fail 
# plt.rcParams.update({
#     "text.usetex": True,
#     "font.family": "Helvetica"
# })

org_var_1_index_start=0
org_var_1_index_end=7
org_var_2_index_start=0
org_var_2_index_end=1

def plot_shear_rate_to_asses_SS(org_var_2_index_end,org_var_2_index_start,org_var_1_index_start,org_var_1_index_end,no_timesteps,phi,lengthscale,timestep_points,scaled_temp,number_of_solutions,org_var_1,org_var_2,shear_rate_upper,shear_rate_lower,fluid_name,box_size_nd):
    for z in range(0,number_of_solutions): 
        #for k in range(org_var_2_index_start,org_var_2_index_end):
        for m in range(org_var_1_index_start,org_var_1_index_end):
             for k in range(org_var_2_index_start,org_var_2_index_end):
                plt.plot(timestep_points[0,0,0,:],shear_rate_upper[z,m,k,:])
                plt.plot(timestep_points[0,0,0,:],shear_rate_lower[z,m,k,:])
                plt.xlabel('$N_{t}[-]$')
                plt.ylabel('$\dot{\gamma}[\\tau]$',rotation='horizontal')
                plt.title(fluid_name+" simulation run with all $f_{v,x}$ and all $N_{v,x}$, $\\bar{T}="+str(scaled_temp)+"$, $L/\ell="+str(box_side_length_scaled[0,z])+"$")
                #plt.title(fluid_name+" simulation run with all $K$ and $f_{v,x}=$"+str(org_var_1[m])+", $\\bar{T}="+str(scaled_temp)+"$, $\ell="+str(lengthscale)+"$")
                
        plt.show()
        #plot_save=input("save figure?, YES/NO")
        # if plot_save=='YES':
        #     plt.savefig(fluid_name+'_T_'+str(scaled_temp)+'_length_scale_'+str(lengthscale)+'_phi_'+str(phi)+'_no_timesteps_'+str(no_timesteps)+'.png')
        # else:
        #     print('Thanks for checking steady state')

plot_shear_rate_to_asses_SS(org_var_2_index_end,org_var_2_index_start,org_var_1_index_start,org_var_1_index_end,no_timesteps,phi,lengthscale,timestep_points,scaled_temp,number_of_solutions,org_var_1,org_var_2,shear_rate_upper,shear_rate_lower,fluid_name,box_size_nd)
# need to save this plot 
# saving this data 
#%%
name_of_run_for_save=fluid_name+"_phi_"+str(phi)+"_pure_fluid_notsteps_"+str(no_timesteps)+"_"+str(scaled_timestep)+"_scaled_box_size_"+str(np.round(box_side_length_scaled[0][0]))+"_run_"+batchcode
print(name_of_run_for_save)
np.save("timestep_points_"+name_of_run_for_save,timestep_points)
np.save("shear_rate_lower_"+name_of_run_for_save,shear_rate_lower)
np.save("shear_rate_upper_"+name_of_run_for_save,shear_rate_upper)
np.save("pearson_coeff_upper_"+name_of_run_for_save,pearson_coeff_lower)
np.save("pearson_coeff_lower_"+name_of_run_for_save,pearson_coeff_upper)
np.save("VP_data_lower_realisation_averaged_"+name_of_run_for_save,VP_data_lower_realisation_averaged)
np.save("VP_data_upper_realisation_averaged_"+name_of_run_for_save,VP_data_upper_realisation_averaged)
np.save("VP_z_data_lower_"+name_of_run_for_save,VP_z_data_lower)
np.save("VP_z_data_upper_"+name_of_run_for_save,VP_z_data_upper)
np.save("shear_rate_upper_error_"+name_of_run_for_save,shear_rate_upper_error)
np.save("shear_rate_lower_error_"+name_of_run_for_save,shear_rate_lower_error)


#%% loading in data option need to make this run 

name_of_run_for_save=fluid_name+"_phi_"+str(phi)+"_pure_fluid_notsteps_"+str(no_timesteps)+"_"+str(scaled_timestep)+"_scaled_box_size_"+str(np.round(box_side_length_scaled[0][0]))+"_run_"+batchcode
print(name_of_run_for_save)
timestep_points=np.load("timestep_points_"+name_of_run_for_save+".npy")
shear_rate_lower=np.load("shear_rate_lower_"+name_of_run_for_save+".npy")
shear_rate_upper=np.load("shear_rate_upper_"+name_of_run_for_save+".npy")
pearson_coeff_lower=np.load("pearson_coeff_upper_"+name_of_run_for_save+".npy")
pearson_coeff_upper=np.load("pearson_coeff_lower_"+name_of_run_for_save+".npy")
VP_data_lower_realisation_averaged=np.load("VP_data_lower_realisation_averaged_"+name_of_run_for_save+".npy")
VP_data_upper_realisation_averaged=np.load("VP_data_upper_realisation_averaged_"+name_of_run_for_save+".npy")
shear_rate_upper_error=np.load("shear_rate_upper_error_"+name_of_run_for_save+".npy")
shear_rate_lower_error=np.load("shear_rate_lower_error_"+name_of_run_for_save+".npy")
VP_z_data_lower=np.load("VP_z_data_lower_"+name_of_run_for_save+".npy")
VP_z_data_upper=np.load("VP_z_data_upper_"+name_of_run_for_save+".npy")
#np.save(fluid_name+'_VP_z_data_upper_'+str(run_number)+'_phi_'+str(phi)+'_'+str(np.round(box_side_length_scaled[0,0]))+'_T_'+str(scaled_temp)+'_no_timesteps_'+str(no_timesteps),VP_z_data_upper)





# %%
truncation_timestep=200000 # for H20 and Nitrogen 
truncation_and_SS_averaging_data=  truncation_step_and_SS_average_of_VP_and_stat_tests(shear_rate_upper_error,shear_rate_lower_error,timestep_points,pearson_coeff_lower,pearson_coeff_upper,shear_rate_upper,shear_rate_lower,VP_ave_freq,truncation_timestep,VP_data_lower_realisation_averaged,VP_data_upper_realisation_averaged)
standard_deviation_upper_error=truncation_and_SS_averaging_data[0]
standard_deviation_lower_error=truncation_and_SS_averaging_data[1]
pearson_coeff_upper_mean_SS=truncation_and_SS_averaging_data[2]
pearson_coeff_lower_mean_SS=truncation_and_SS_averaging_data[3]
pearson_coeff_mean_SS= (np.abs(pearson_coeff_lower_mean_SS)+np.abs(pearson_coeff_upper_mean_SS))*0.5
shear_rate_lower_steady_state_mean=truncation_and_SS_averaging_data[4]
#print(shear_rate_lower_steady_state_mean)
shear_rate_upper_steady_state_mean=truncation_and_SS_averaging_data[5]
#print(shear_rate_upper_steady_state_mean)
VP_steady_state_data_lower_truncated_time_averaged=truncation_and_SS_averaging_data[6]
VP_steady_state_data_upper_truncated_time_averaged=truncation_and_SS_averaging_data[7]
shear_rate_upper_steady_state_mean_error=truncation_and_SS_averaging_data[8]
#print(shear_rate_upper_steady_state_mean_error)
shear_rate_lower_steady_state_mean_error=truncation_and_SS_averaging_data[9]
#print(shear_rate_lower_steady_state_mean_error)

mean_fitting_error= (np.abs(shear_rate_upper_steady_state_mean_error)+np.abs(shear_rate_lower_steady_state_mean_error))*0.5
#print(mean_fitting_error)
if np.any(mean_fitting_error<0.0005):
    print("All data accepts linear fit")

else:
   
     print("Check curve fitting error")

truncation_and_SS_averaging_data_TP=  truncation_step_and_SS_average_of_VP_and_stat_tests(shear_rate_upper_error,shear_rate_lower_error,timestep_points,pearson_coeff_lower,pearson_coeff_upper,shear_rate_upper,shear_rate_lower,VP_ave_freq,truncation_timestep,TP_data_lower_realisation_averaged,TP_data_upper_realisation_averaged)

TP_steady_state_data_lower_truncated_time_averaged=truncation_and_SS_averaging_data_TP[6]
TP_steady_state_data_upper_truncated_time_averaged=truncation_and_SS_averaging_data_TP[7]

# need to write code that checks the errors 


#%%plotting qll 4 SS V_Ps
# need to fix legend location 
plt.rcParams.update({'font.size': 25})
org_var_1_choice_index=org_var_1.size
fontsize=35
labelpadx=15
labelpady=35
width_plot=10
height_plot=6
legend_x_pos=1
legend_y_pos=1
org_var_1_index_start=0
org_var_1_index_end=7
org_var_2_index_start=0
org_var_2_index_end=1
# need to add all these settings for every plot
def plotting_SS_velocity_profiles(org_var_2_index_start,org_var_1_index_end,legend_x_pos, legend_y_pos,labelpadx,labelpady,fontsize,number_of_solutions,org_var_1_choice_index,width_plot,height_plot,org_var_1,org_var_2,VP_ave_freq,no_timesteps,VP_steady_state_data_lower_truncated_time_averaged,VP_steady_state_data_upper_truncated_time_averaged,VP_z_data_lower,VP_z_data_upper):
    for z in range(0,number_of_solutions):
    
        for m in range(0,org_var_2.size):
        #for k in range(0,org_var_1.size):  
            
            fig=plt.figure(figsize=(width_plot,height_plot))
            gs=GridSpec(nrows=1,ncols=1)

            ax1= fig.add_subplot(gs[0,0])
    
        


            for k in range(0,org_var_1.size):  
                x_1=VP_steady_state_data_lower_truncated_time_averaged[z,k,m,:]
                #print(x_1.shape)
                x_2=VP_steady_state_data_upper_truncated_time_averaged[z,k,m,:]
                y_1=VP_z_data_lower[z,0,:]
                #print(y_1.shape)
                y_2=VP_z_data_upper[z,0,:]
                print(k)
                #for i in range(org_var_2_index_start,org_var_1_index_end):
                
                ax1.plot(y_1[:],x_1[:],label='$f_p=${}'.format(org_var_1[k]),marker='x')
                ax1.set_ylabel('$v_{x}\ [\\frac{\\tau}{\ell}]$',rotation=0,labelpad=labelpady )
                ax1.set_xlabel('$L_{z}\ [\ell^{-1}]$',rotation=0,labelpad=labelpadx,)
                ax1.legend(frameon=False,loc=0,bbox_to_anchor=(legend_x_pos, legend_y_pos))       
        plt.show()
    

plotting_SS_velocity_profiles(org_var_2_index_start,org_var_1_index_end,legend_x_pos, legend_y_pos,labelpadx,labelpady,fontsize,number_of_solutions,org_var_1_choice_index,width_plot,height_plot,org_var_1,org_var_2,VP_ave_freq,no_timesteps,VP_steady_state_data_lower_truncated_time_averaged,VP_steady_state_data_upper_truncated_time_averaged,VP_z_data_lower,VP_z_data_upper)

# could probably vectorise this or use a method 
# error_count = 0
# for z in range(0,number_of_solutions):
#     for k in range(org_var_1_index_start,org_var_1_index_end):
#             for m in range(org_var_2_index_start,org_var_2_index_end):
                 
                 
#                  if pearson_coeff_mean_SS[z,k,m]<0.7:
#                      print('Non-linear simulation run please inspect')
#                      error_count=error_count +1 
#                  else:
#                      print('Great success')
                     
  
                    
# print('Non-linear simulation count: ',error_count)
# marker=['x','o','+','^',"1","X","d","*","P","v"]
# for z in range(0,number_of_solutions):
#     for k in range(org_var_1_index_start,org_var_1_index_end):
#             for m in range(org_var_2_index_start,org_var_2_index_end):
#               plt.scatter(org_var_2[m],pearson_coeff_mean_SS[z,k,m],marker=marker[k])
#               plt.xlabel('$f_{v,x}[-]$')
#               #plt.xlabel('$K[\\frac{\\tau}{\mu}]$')
#               #plt.xscale('log')
#               plt.ylabel('$P_{C}[-]$',rotation=0,labelpad=30)
#     #plt.legend(loc=7,bbox_to_anchor=(1.3, 0.5))
              
#     plt.show()

# print('Non-linear simulation count: ',error_count)
                

#%% checking grad of datta
#assess gradient of truncated shear rate data to determine steady state
# can then truncate again 
slope_shear_rate_upper=  np.zeros((number_of_solutions,org_var_1.size,org_var_2.size))
slope_shear_rate_lower=  np.zeros((number_of_solutions,org_var_1.size,org_var_2.size))

gradient_tolerance= 5e-9
for z in range(0,number_of_solutions): 
        for m in range(org_var_1_index_start,org_var_1_index_end):
            for k in range(org_var_2_index_start,org_var_2_index_end):
                slope_shear_rate_upper[z,m,k]=np.polyfit(timestep_points[0,0,0,:],shear_rate_upper[z,m,k,:],1)[0]
                slope_shear_rate_lower[z,m,k]=np.polyfit(timestep_points[0,0,0,:],shear_rate_upper[z,m,k,:],1)[0]
                if np.abs(slope_shear_rate_upper[z,m,k]) < gradient_tolerance:
                    slope_shear_rate_upper[z,m,k] =slope_shear_rate_upper[z,m,k] 
                else: 
                    #slope_shear_rate_upper[z,m,k]='NaN'
                    print('FAILED run, exclude from data ')
                if np.abs(slope_shear_rate_lower[z,m,k]) < gradient_tolerance:
                    slope_shear_rate_lower[z,m,k] =slope_shear_rate_lower[z,m,k] 
                else: 
                    #slope_shear_rate_lower[z,m,k]='NaN'
                    print('FAILED run, exclude from data ')
print("if no fail statements, data can be considered steady")

# plotting gradient of the shear vs time plot 
for z in range(0,number_of_solutions): 
     #for m in range(org_var_1_index_start,org_var_1_index_end):
        #for k in range(org_var_2_index_start,org_var_2_index_end):
           # plt.yscale('log')
            plt.ylabel(' $d \dot{\gamma}/d t\ [1/\\tau^{2}]$',rotation=0)
            plt.xlabel('$f_{v,x}[-]$')
            #plt.xlabel('$K[\\frac{\\tau}{\mu}]$')
            #plt.xscale('log')
            plt.scatter(org_var_1[:],slope_shear_rate_upper[z,:,0])
            plt.scatter(org_var_1[:],slope_shear_rate_lower[z,:,0])
            #plt.title("Needs a title")
plt.show




# importing momentum after steady state
def mom_data_averaging_and_flux_calc(box_size_key,number_of_solutions,org_var_1,truncation_timestep,org_var_2,scaled_timestep,no_timesteps,box_side_length_scaled,mom_data):
    mom_data_realisation_averaged=()
    number_swaps_before_truncation=(np.ceil(truncation_timestep/swap_rate)).astype(int)
    mom_data_realisation_averaged_truncated=()
    flux_x_momentum_z_direction=np.zeros((number_of_solutions,org_var_1.size,org_var_2.size))
    total_run_time=scaled_timestep* (no_timesteps-truncation_timestep)
    
    flux_ready_for_plotting=np.zeros((number_of_solutions,org_var_1.size,org_var_2.size))
    for z in range(0,number_of_solutions):  
        box_area_nd=float(box_size_key[z])**2
        for j in range(0,org_var_1.size):
               
                mom_data_realisation_averaged=mom_data_realisation_averaged+(np.mean(mom_data[j],axis=2),)
                mom_data_realisation_averaged_truncated=mom_data_realisation_averaged_truncated+(mom_data_realisation_averaged[j][:,:,number_swaps_before_truncation[j]:],)
                for i in range(0,org_var_2.size):
                    


            #for i in range(0,org_var_2.size):

                    #mom_data_realisation_averaged_truncated=mom_data_realisation_averaged_truncated+(mom_data_realisation_averaged[j][:,:,number_swaps_before_truncation[i]:],)
                    #mom_data_realisation_averaged_truncated=mom_data_realisation_averaged_truncated+(mom_data_realisation_averaged[j][:,:,number_swaps_before_truncation[j]:],)
                    #print(mom_data_realisation_averaged_truncated.shape)


            # now apply the MP formula 
                    mom_difference= mom_data_realisation_averaged_truncated[j][z,i,-1]-mom_data_realisation_averaged_truncated[j][z,i,0]
    #                 print(mom_difference)
                    flux_x_momentum_z_direction[z,j,i]=(mom_difference)/(2*total_run_time*float(box_area_nd))
                
    flux_ready_for_plotting=np.log((np.abs(flux_x_momentum_z_direction)))
    
    return flux_ready_for_plotting,mom_data_realisation_averaged_truncated
#%%
flux_ready_for_plotting=mom_data_averaging_and_flux_calc(box_size_key,number_of_solutions,org_var_1,truncation_timestep,org_var_2,scaled_timestep,no_timesteps,box_side_length_scaled[0,0],mom_data)[0]
mom_data_realisation_averaged_truncated=mom_data_averaging_and_flux_calc(box_size_key,number_of_solutions,org_var_1,truncation_timestep,org_var_2,scaled_timestep,no_timesteps,box_side_length_scaled[0,0],mom_data)[1]



shear_rate_mean_of_both_cells=(((np.abs(shear_rate_lower_steady_state_mean)+np.abs(shear_rate_upper_steady_state_mean))*0.5))
shear_rate_mean_error_of_both_cells=(np.abs(shear_rate_lower_steady_state_mean_error)+np.abs(shear_rate_upper_steady_state_mean_error))*0.5
print(shear_rate_mean_of_both_cells.shape)
print(shear_rate_mean_error_of_both_cells.shape)
shear_rate_mean_error_of_both_cells_relative=shear_rate_mean_error_of_both_cells/shear_rate_mean_of_both_cells
shear_rate_mean_of_both_cells=np.log(((np.abs(shear_rate_lower_steady_state_mean)+np.abs(shear_rate_upper_steady_state_mean))*0.5))
shear_rate_mean_error_of_both_cells=shear_rate_mean_of_both_cells*shear_rate_mean_error_of_both_cells_relative

print(shear_rate_mean_of_both_cells.shape)
print(shear_rate_mean_error_of_both_cells.shape)

flux_vs_shear_regression_line_params=()
x=shear_rate_mean_of_both_cells
#shear_rate_mean_of_both_cells=np.reshape(shear_rate_mean_of_both_cells,(flux_ready_for_plotting.shape))
# fiting params
def func4(x, a, b):
   #return np.log(a) + np.log(b*x)
   #return (a*(x**b))
   #return 10**(a*np.log(x) + b)
   return (a*x) +b 
   #return a*np.log(b*x)+c



org_var_1_fitting_start_index=0
org_var_1_fitting_end_index=4
size_of_new_data=org_var_1_fitting_end_index-org_var_1_fitting_start_index
#shear_rate_error_of_both_cell_mean_over_all_points_relative = shear_rate_mean_error_of_both_cells[z,org_var_1_fitting_start_index:org_var_1_fitting_end_index,:]/shear_rate_mean_of_both_cells[z,org_var_1_fitting_start_index:org_var_1_fitting_end_index,:]
shear_rate_mean_error_of_both_cell_mean_over_selected_points_relative= np.zeros((box_side_length_scaled.size))
# mean_flux_ready_for_plotting=np.mean(flux_ready_for_plotting[z,org_var_1_fitting_start_index:org_var_1_fitting_end_index,:],axis=1)
# mean_flux_ready_for_plotting_relative_error=np.zeros((org_var_2.size))
# mean_error_in_fit =np.zeros((org_var_2.size))
y_residual_in_fit=np.zeros((number_of_solutions,size_of_new_data,org_var_2.size))
for z in range(0,number_of_solutions):    
    shear_rate_mean_error_of_both_cell_mean_over_selected_points_relative[z]= np.mean(shear_rate_mean_error_of_both_cells_relative[z,org_var_1_fitting_start_index:org_var_1_fitting_end_index,:],axis=0)

    for i in range(0,org_var_2.size):
        
        flux_vs_shear_regression_line_params= flux_vs_shear_regression_line_params+(scipy.optimize.curve_fit(func4,shear_rate_mean_of_both_cells[z,org_var_1_fitting_start_index:org_var_1_fitting_end_index,i],flux_ready_for_plotting[z,org_var_1_fitting_start_index:org_var_1_fitting_end_index,i],method='lm',maxfev=5000)[0],)
        y_residual_in_fit[z,:,i]=func4(shear_rate_mean_of_both_cells[z,org_var_1_fitting_start_index:org_var_1_fitting_end_index,i],flux_vs_shear_regression_line_params[i][0] ,flux_vs_shear_regression_line_params[i][1])-flux_ready_for_plotting[z,org_var_1_fitting_start_index:org_var_1_fitting_end_index,i]
        
        #mean_error_in_fit[i] = np.sqrt(np.mean((func4(shear_rate_mean_of_both_cells[z,org_var_1_fitting_start_index:org_var_1_fitting_end_index,i],flux_vs_shear_regression_line_params[i][0] ,flux_vs_shear_regression_line_params[i][1])-flux_ready_for_plotting[z,org_var_1_fitting_start_index:org_var_1_fitting_end_index,i])**2))
        #mean_flux_ready_for_plotting_relative_error[i]=mean_error_in_fit[i]/mean_flux_ready_for_plotting[i]
        #print(scipy.optimize.curve_fit(func4,shear_rate_mean_of_both_cells[z,:,i],flux_ready_for_plotting[z,i,:],method='lm',maxfev=5000)[0])

params=flux_vs_shear_regression_line_params
relative_y_residual_mean= np.mean(y_residual_in_fit/flux_ready_for_plotting[z,org_var_1_fitting_start_index:org_var_1_fitting_end_index,:],axis=1)

total_error_relative_in_flux_fit= relative_y_residual_mean+shear_rate_mean_error_of_both_cell_mean_over_selected_points_relative

#%% px vs time
#calculating error of flux
# plot cumulative momentum exchange vs time 
# fit to linear grad and take error 
# need to calculate number of swaps done, plot that as time axes 
#
#total_number_of_swaps_after_SS=(np.floor( (no_timesteps-truncation_timestep)/org_var_2))
swap_timestep_vector=()
total_run_time=scaled_timestep* (no_timesteps-truncation_timestep)
for z in range(0,swap_rate.size):
    total_number_of_swaps_after_SS=mom_data_realisation_averaged_truncated[z].shape[2]
    final_swap_step= truncation_timestep +(total_number_of_swaps_after_SS*swap_rate[z])
    #print(final_swap_step)
    swap_timestep_vector= swap_timestep_vector+ (np.arange(truncation_timestep,final_swap_step,int(swap_rate[z])),)


slope_momentum_vector_error=()
slope_momentum_vector_error_1=()
pearson_coeff_momentum=()
slope_momentum_vector_mean_abs_error= np.zeros((number_of_solutions,org_var_1_index_end,org_var_1_index_end))
slope_flux_abs_error=np.zeros((number_of_solutions,org_var_1_index_end,org_var_1_index_end))
for z in range(0,number_of_solutions):
    box_area_nd=float(box_size_key[z])**2
    #for k in range(org_var_1_index_start,org_var_1_index_end):
    for m in range(org_var_2_index_start,org_var_2_index_end):
            for k in range(org_var_1_index_start,org_var_1_index_end): 
                plt.scatter(swap_timestep_vector[k],-mom_data_realisation_averaged_truncated[k][z,m,:],label='$f_v=${}'.format(org_var_1[k]),marker='x', s=0.00005)
                plt.legend()
                plt.ylabel('$P_x$',rotation=0)
                plt.xlabel('$N_t$')
                
                #slope_momentum_vector_error=slope_momentum_vector_error + (np.polyfit(swap_timestep_vector[m],-mom_data_realisation_averaged_truncated[m][z,k,:],1,full=True)[1],)
                #slope_momentum_vector_error_1=slope_momentum_vector_error_1 + (scipy.stats.linregress(swap_timestep_vector[m],-mom_data_realisation_averaged_truncated[m][z,k,:] ).stderr,)
                pearson_coeff_momentum=pearson_coeff_momentum+ (scipy.stats.pearsonr(swap_timestep_vector[k],-mom_data_realisation_averaged_truncated[k][z,m,:])[0],)
                if pearson_coeff_momentum[m]  > 0.9999:
                    print('All pearson coeffs are perfectly linear, therefore there is no error in the total momentum')
                else:
                    print('Cumulative total momentum is not linear in time, please check data is has reached SS')
                #scipy.stats.linregress(swap_timestep_vector[m],-mom_data_realisation_averaged_truncated[m][z,k,:] ).stderr
                # print(mom_data_realisation_averaged_truncated[m][z,k,:].shape[0])
                # slope_momentum_vector_mean_abs_error[z,k,m]= np.sqrt(slope_momentum_vector_error[m][0]/mom_data_realisation_averaged_truncated[m][z,k,:].shape[0])
                # slope_flux_abs_error[z,k,m]=slope_momentum_vector_mean_abs_error[z,k,m]/(2*total_run_time*float(box_area_nd))
                #print(swap_timestep_vector[m].shape,mom_data_realisation_averaged_truncated[m][z,k,:].shape)
            plt.show()



#%%

#save_string_for_plot= 'Flux_vs_shear_rate_'+fluid_name+'_phi_range_'+str(phi[0])+'_'+str(phi[1])+'_l_scale_'+str(lengthscale)+'_T_'+str(scaled_temp)+'.png'
labelpadx=15
labelpady=55
fontsize=20
count=1
org_var_1_index=org_var_1_fitting_start_index
org_var_2_index=1
plt.rcParams.update({'font.size': 15})

       
shear_viscosity=[]
shear_viscosity_abs_error=[]
gradient_of_fit=[]
       
#plotting_flux_vs_shear_rate(func4,labelpadx,labelpady,params,fontsize,box_side_length_scaled,number_of_solutions,flux_ready_for_plotting,org_var_1_index,shear_rate_mean_of_both_cells)
def plotting_flux_vs_shear_rate(shear_rate_mean_error_of_both_cells,func4,labelpadx,labelpady,params,fontsize,box_side_length_scaled,number_of_solutions,flux_ready_for_plotting,org_var_1_index,shear_rate_mean_of_both_cells):
    
    for z in range(0,number_of_solutions):
        
        
        x=shear_rate_mean_of_both_cells[z,org_var_1_fitting_start_index:org_var_1_fitting_end_index,:]
        x_pos_error=np.abs(shear_rate_mean_error_of_both_cells[z,org_var_1_fitting_start_index:org_var_1_fitting_end_index,:])
        #y_pos_error=np.abs(abs_error_in_flux[z,:,:])
        y=flux_ready_for_plotting[z,org_var_1_fitting_start_index:org_var_1_fitting_end_index,:]
        
        for i in range(0,org_var_2_index):
        
        #for i in range(0,1):
            #if z==0:
                j=i
                
                # need to add legend to this 
                plt.scatter(x[:,i],y[:,i],label='$L=${}'.format(np.around(box_side_length_scaled[0,z]),decimals=0),marker='x')
                plt.errorbar(x[:,i],y[:,i],xerr=x_pos_error[:,i],ls ='',capsize=3,color='r')
                plt.plot(x[:,i],func4(x[:,i],params[z][0],params[z][1]))
                #plt.fill_between(y[:,i], x_neg_error[i,:], x_pos_error[i,:])
                #plt.xscale('log')
                plt.xlabel('$log(\dot{\gamma}\\tau)$', labelpad=labelpadx,fontsize=fontsize)
                #plt.yscale('log')
                plt.ylabel('$log(J_{z}(p_{x})$$\ \\frac{\\tau^{3}}{\\varepsilon})$',rotation=0,labelpad=labelpady,fontsize=fontsize)
                plt.legend()
                #plt.show() 
                shear_viscosity_=10** (params[z][1])
                shear_viscosity.append(shear_viscosity_)
                shear_viscosity_abs_error.append(shear_viscosity_*total_error_relative_in_flux_fit[z,i])
                
                grad_fit=(params[z][0])
                grad_fit_abs_error= grad_fit*shear_rate_mean_error_of_both_cell_mean_over_selected_points_relative[z]
                gradient_of_fit.append(grad_fit)
                print('Dimensionless_shear_viscosity:',shear_viscosity_,',abs error',shear_viscosity_abs_error)
                print('Grad of fit =',grad_fit,',abs error', grad_fit_abs_error)
                plt.show() 

    
           
        
                    
plotting_flux_vs_shear_rate(shear_rate_mean_error_of_both_cells,func4,labelpadx,labelpady,params,fontsize,box_side_length_scaled,number_of_solutions,flux_ready_for_plotting,org_var_1_index,shear_rate_mean_of_both_cells)    
# need to adjust this so we get the visocsities of both plots 
# shear_viscosity=10** (params[0][1])
# grad_fit=(params[0][0])
# print('Dimensionless_shear_viscosity:',shear_viscosity)
# print('Grad of fit =',grad_fit)
# to get the error in viscosity need to look whether we take the mean of the relative or absolute errors. 

#dimensionful_shear_viscosity= shear_viscosity * mass_scale / lengthscale*timescale
#plotting qll 4 SS V_Ps



#%%
# need to fix legend location 
plt.rcParams.update({'font.size': 25})
org_var_1_choice_index=org_var_1.size
fontsize=35
labelpadx=15
labelpady=35
width_plot=15
height_plot=10
legend_x_pos=1
legend_y_pos=1
org_var_1_index_start=0
org_var_1_index_end=7
org_var_2_index_start=0
org_var_2_index_end=1
# need to add all these settings for every plot
def plotting_SS_velocity_profiles(org_var_2_index_start,org_var_1_index_end,legend_x_pos, legend_y_pos,labelpadx,labelpady,fontsize,number_of_solutions,org_var_1_choice_index,width_plot,height_plot,org_var_1,org_var_2,VP_ave_freq,no_timesteps,VP_steady_state_data_lower_truncated_time_averaged,VP_steady_state_data_upper_truncated_time_averaged,VP_z_data_lower,VP_z_data_upper):
    for z in range(0,number_of_solutions):
    
        for m in range(0,org_var_2.size):
        #for k in range(0,org_var_1.size):  
            
            fig=plt.figure(figsize=(width_plot,height_plot))
            gs=GridSpec(nrows=1,ncols=1)

            ax1= fig.add_subplot(gs[0,0])
    
        


            for k in range(0,org_var_1.size):  
                x_1=VP_steady_state_data_lower_truncated_time_averaged[z,k,m,:]
                #print(x_1.shape)
                x_2=VP_steady_state_data_upper_truncated_time_averaged[z,k,m,:]
                y_1=VP_z_data_lower[z,0,:]
                #print(y_1.shape)
                y_2=VP_z_data_upper[z,0,:]
                print(k)
                #for i in range(org_var_2_index_start,org_var_1_index_end):
                
                ax1.plot(y_1[:],x_1[:],label='$f_p=${}'.format(org_var_1[k]),marker='x')
                ax1.set_ylabel('$v_{x}\ [\\frac{\\tau}{\ell}]$',rotation=0,labelpad=labelpady, fontsize=fontsize)
                ax1.set_xlabel('$L_{z}\ [\ell^{-1}]$',rotation=0,labelpad=labelpadx,fontsize=fontsize)
                ax1.legend(frameon=False,loc=0,bbox_to_anchor=(legend_x_pos, legend_y_pos),fontsize=fontsize-4)       
        plt.show()
    

plotting_SS_velocity_profiles(org_var_2_index_start,org_var_1_index_end,legend_x_pos, legend_y_pos,labelpadx,labelpady,fontsize,number_of_solutions,org_var_1_choice_index,width_plot,height_plot,org_var_1,org_var_2,VP_ave_freq,no_timesteps,VP_steady_state_data_lower_truncated_time_averaged,VP_steady_state_data_upper_truncated_time_averaged,VP_z_data_lower,VP_z_data_upper)




#%% plotting temp profiles 
plt.rcParams.update({'font.size': 25})
org_var_1_choice_index=org_var_1.size
fontsize=45
labelpadx=15
labelpady=45
width_plot=12
height_plot=7
legend_x_pos=1
legend_y_pos=0.8
org_var_1_index_start=0
org_var_1_index_end=7
org_var_2_index_start=0
org_var_2_index_end=1
def plotting_SS_Temp_profiles(org_var_2_index_start,org_var_1_index_end,legend_x_pos, legend_y_pos,labelpadx,labelpady,fontsize,number_of_solutions,org_var_1_choice_index,width_plot,height_plot,org_var_1,org_var_2,VP_ave_freq,no_timesteps,TP_steady_state_data_lower_truncated_time_averaged,TP_steady_state_data_upper_truncated_time_averaged,TP_z_data_lower,TP_z_data_upper):
    for z in range(0,number_of_solutions):
    
        for m in range(0,org_var_2.size):
        #for k in range(0,org_var_1.size):  
            
            fig=plt.figure(figsize=(width_plot,height_plot))
            gs=GridSpec(nrows=1,ncols=2)

            ax1= fig.add_subplot(gs[0,1])
            ax2= fig.add_subplot(gs[0,0])
    
        


            for k in range(org_var_1_index_start,org_var_1_index_end):  
                x_1=TP_steady_state_data_lower_truncated_time_averaged[z,k,m,:]
                #print(x_1.shape)
                x_2=TP_steady_state_data_upper_truncated_time_averaged[z,k,m,:]
                y_1=TP_z_data_lower[z,0,:]
                #print(y_1.shape)
                y_2=TP_z_data_upper[z,0,:]
                #print(k)
                #for i in range(org_var_2_index_start,org_var_1_index_end):
                
                ax1.plot(y_1[:],x_1[:],label='$f_p=${}'.format(org_var_1[k]),marker='x')
                #ax1.set_yscale('log')
                #ax2.set_yscale('log')
                #ax1.set_ylabel('$v_{x}\ [\\frac{\\tau}{\ell}]$',rotation=0,labelpad=labelpady, fontsize=fontsize)
                ax1.set_xlabel('$L_{z}/\ell$',rotation=0,labelpad=labelpadx,fontsize=fontsize)
                ax2.plot(y_2[:],x_2[:],label='$f_p=${}'.format(org_var_1[k]),marker='x')
                ax2.set_ylabel('$ T\\frac{ k_{B}}{\epsilon}$',rotation=0,labelpad=labelpady, fontsize=fontsize)
                ax2.set_xlabel('$L_{z}/\ell$',rotation=0,labelpad=labelpadx,fontsize=fontsize)
                ax1.legend(frameon=False,loc=0,bbox_to_anchor=(legend_x_pos, legend_y_pos))      
            plt.savefig(fluid_name+"_temp_profile_batch_"+str(batchcode)+".pdf",dpi=500, bbox_inches='tight')
            plt.show()
    

plotting_SS_Temp_profiles(org_var_2_index_start,org_var_1_index_end,legend_x_pos, legend_y_pos,labelpadx,labelpady,fontsize,number_of_solutions,org_var_1_choice_index,width_plot,height_plot,org_var_1,org_var_2,VP_ave_freq,no_timesteps,TP_steady_state_data_lower_truncated_time_averaged,TP_steady_state_data_upper_truncated_time_averaged,TP_z_data_lower,TP_z_data_upper)
#%% all flux vs shear
labelpadx=15
labelpady=60
fontsize=20
count=1
org_var_1_index=org_var_1_fitting_start_index
org_var_2_index=1
plt.rcParams.update({'font.size': 15})

# shear_viscosity=[]
gradient_of_fit=[]

flux_fitting_params=flux_vs_shear_regression_line_params

#for i in range(0,org_var_2_index):

        
i=0
for z in range(0,box_side_length_scaled.size):
    x=shear_rate_mean_of_both_cells[z,org_var_1_fitting_start_index:org_var_1_fitting_end_index,:]
    y=flux_ready_for_plotting[z,org_var_1_fitting_start_index:org_var_1_fitting_end_index,:]



#   shear_viscosity_=10** (flux_fitting_params[z,i,1])
#   shear_viscosity_abs_error = shear_viscosity_*total_error_relative_in_flux_fit[z,i]
    
    grad_fit=(params[z][0])
    # grad_fit_abs_error= grad_fit*shear_rate_mean_error_of_both_cell_mean_over_selected_points_relative[z,i]
    # print('Dimensionless_shear_viscosity:',shear_viscosity_,',abs error',shear_viscosity_abs_error)
    
    #print('Grad of fit =',grad_fit,',abs error', grad_fit_abs_error)
    plt.scatter(x[:,i],y[:,i],label="$L/\ell=$"+str(box_side_length_scaled[0,z])+", grad$=$"+str(sigfig.round(grad_fit,sigfigs=2)))#+"$\pm$"+str(sigfig.round(grad_fit_abs_error,sigfigs=1)),marker='x')
    plt.plot(x[:,i],func4(x[:,i],params[z][0],params[z][1]),'--')
    plt.xlabel('$log(\dot{\gamma}\\tau)$', labelpad=labelpadx,fontsize=fontsize)
    plt.ylabel('$log(J_{z}(p_{x})$$\ \\frac{\\tau^{3}}{\\varepsilon})$',rotation=0,labelpad=labelpady,fontsize=fontsize)
    plt.legend(loc='upper right',bbox_to_anchor=(0.25,-0.1))
    #plt.legend(loc='best')
#plt.tight_layout()
#plt.savefig(fluid_name+"_flux_vs_shear_swap_rates_"+str(org_var_1[org_var_1_fitting_start_index])+"_"+str(org_var_1[org_var_1_fitting_end_index-1])+"_run_number_"+str(run_number[0])+"_"+str(run_number[1])+"_"+str(run_number[2])+".pdf",dpi=500, bbox_inches='tight')

plt.show() 
     
#%%
##%% shear viscosity vs box size
# need to add error bars to this 
labelpadx=5
labelpady=15
#shear_viscosity_abs_error_max=np.amax(shear_viscosity_abs_error,axis=0)
for z in range(0,1):
          x=box_side_length_scaled[0,:]
          y=shear_viscosity[:]
     
          #plt.scatter(x[:,i],y[:,i],label="$L=$"+str(box_side_length_scaled[z])+", grad$=$"+str(sigfig.round(grad_fit,sigfigs=2))+"$\pm$"+str(sigfig.round(grad_fit_abs_error,sigfigs=1)),marker='x')
          plt.plot(x,y,"--",marker= 'x')#label="$N_{v,x}=$"+str(org_var_2[z])+", $\Delta\eta_{max}=$"+str(sigfig.round(shear_viscosity_abs_error_max[z],sigfigs=2)),marker='x')
          plt.xlabel('$L/\ell$', labelpad=labelpadx,fontsize=fontsize)
          #plt.yscale('log')
          #plt.xscale('log')
          plt.ylabel('$\eta \\frac{\ell^{3}}{\epsilon\\tau}$',rotation=0,labelpad=labelpady,fontsize=fontsize)
          plt.legend()
plt.tight_layout()     
#plt.savefig(fluid_name+"_shear_eta_vs_phi_"+str(org_var_1[org_var_1_fitting_start_index])+"_"+str(org_var_1[org_var_1_fitting_end_index-1])+"_run_number_"+str(run_number[0])+"_"+str(run_number[1])+"_"+str(run_number[2])+".pdf",dpi=500, bbox_inches='tight')
plt.show() 
# %% saving all the arrays which are needed for plots
# need to save orginal untruncated VP / shear rate data 

# logged shear rate 
#np.save(fluid_name+'_logged_shear_rate_mean_both_cells_'+str(run_number)+'_phi_'+str(phi)+'_'+str(np.round(box_side_length_scaled[0,0]))+'_T_'+str(scaled_temp)+'_no_timesteps_'+str(no_timesteps),shear_rate_mean_of_both_cells)
np.save("shear_rate_mean_of_both_cells_"+name_of_run_for_save,shear_rate_mean_of_both_cells)

#  shear rate errors 
#np.save(fluid_name+'_logged_shear_rate_mean_error_both_cells_'+str(run_number)+'_phi_'+str(phi)+'_'+str(np.round(box_side_length_scaled[0,0]))+'_T_'+str(scaled_temp)+'_no_timesteps_'+str(no_timesteps),shear_rate_mean_error_of_both_cells)
np.save("shear_rate_mean_error_of_both_cells_"+name_of_run_for_save,shear_rate_mean_error_of_both_cells)

# fitting parameters and viscosity 

#np.save(fluid_name+'_fitting_params_'+str(run_number)+'_phi_'+str(phi)+'_'+str(np.round(box_side_length_scaled[0,0]))+'_T_'+str(scaled_temp)+'_no_timesteps_'+str(no_timesteps),params)
np.save("flux_fitting_params_"+name_of_run_for_save,params)

# flux ready for plotting 

#np.save(fluid_name+'_flux_ready_for_plotting_'+str(run_number)+'_phi_'+str(phi)+'_'+str(np.round(box_side_length_scaled[0,0]))+'_T_'+str(scaled_temp)+'_no_timesteps_'+str(no_timesteps),flux_ready_for_plotting)
np.save("flux_ready_for_plotting_"+name_of_run_for_save,flux_ready_for_plotting)

# steady state velocity profiles 
# v_x data upper/ lower 
#np.save(fluid_name+'_VP_steady_state_data_lower_truncated_time_averaged_'+str(run_number)+'_phi_'+str(phi)+'_'+str(np.round(box_side_length_scaled[0,0]))+'_T_'+str(scaled_temp)+'_no_timesteps_'+str(no_timesteps),VP_steady_state_data_lower_truncated_time_averaged)
np.save("VP_steady_state_data_lower_truncated_time_averaged_"+name_of_run_for_save,VP_steady_state_data_lower_truncated_time_averaged)

#np.save(fluid_name+'_VP_steady_state_data_upper_truncated_time_averaged_'+str(run_number)+'_phi_'+str(phi)+'_'+str(np.round(box_side_length_scaled[0,0]))+'_T_'+str(scaled_temp)+'_no_timesteps_'+str(no_timesteps),VP_steady_state_data_upper_truncated_time_averaged)
np.save("VP_steady_state_data_upper_truncated_time_averaged_"+name_of_run_for_save,VP_steady_state_data_upper_truncated_time_averaged)

# z coordinate upper/lower
#np.save(fluid_name+'_VP_z_data_lower_'+str(run_number)+'_phi_'+str(phi)+'_'+str(np.round(box_side_length_scaled[0,0]))+'_T_'+str(scaled_temp)+'_no_timesteps_'+str(no_timesteps),VP_z_data_lower)
np.save("VP_z_data_lower_"+name_of_run_for_save,VP_z_data_lower)

#np.save(fluid_name+'_VP_z_data_upper_'+str(run_number)+'_phi_'+str(phi)+'_'+str(np.round(box_side_length_scaled[0,0]))+'_T_'+str(scaled_temp)+'_no_timesteps_'+str(no_timesteps),VP_z_data_upper)
np.save("VP_z_data_upper_"+name_of_run_for_save,VP_z_data_upper)



# %%
