##!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script will calculate the MPCD stress tensor for a pure fluid under forward NEMD using hdf5 files 
"""
#%% Importing packages
import os
from random import sample
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import regex as re
import pandas as pd
import sigfig
plt.rcParams.update(plt.rcParamsDefault)
plt.rcParams['text.usetex'] = True
#from mpl_toolkits import mplot3d
from matplotlib.gridspec import GridSpec
import scipy.stats
from datetime import datetime
import h5py as h5 
import multiprocessing as mp


path_2_post_proc_module= '/Volumes/Backup Plus 1/PhD_/Rouse Model simulations/Using LAMMPS imac/LAMMPS python run and analysis scripts/Analysis codes'
#os.chdir(path_2_post_proc_module)
from log2numpy import *
from mom2numpy import *
from velP2numpy import *
from dump2numpy import * 
import glob 
from post_MPCD_MP_processing_module import *
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

#%% key inputs 
# no_SRD=1038230
# box_size=47
# no_SRD=506530
# box_size=37
# no_SRD=121670
# box_size=23
# no_SRD=270
# box_size=3
# no_SRD=58320
# # box_size=18
# no_SRD=2160
# box_size=6
# no_SRD=2560
# box_size=8
rho=5
box_size=34
no_SRD=int((box_size**3)*rho)
#nu_bar=3
#delta_t_srd=0.014872025172594354
#nu_bar=0.9 
#delta_t_srd=0.05674857690605889
delta_t_srd=0.05071624521210362

box_vol=box_size**3
#erate= np.array([0.01,0.001,0.0001])
# #erate=np.array([0.01])
#erate=np.array([0.001,0.002,0.003])

bending_stiffness=np.array([10000]) # original 50,100,200,400
internal_stiffness=np.array([60,100])
#internal_stiffness=np.array([100])
#erate= np.array([0.1,0.01,0.005,0.002,0.001,0.0008])
#no_timesteps=np.array([ 355000,  3549000,  7098000, 17746000, 35492000, 44364000])
no_timesteps=np.array([5915000,  6760000,  7887000,  9464000, 11831000 ])
#no_timesteps=np.array([5915000,  7887000,  9464000, 11831000 ])
erate= np.array([0.02,0.0175,0.015,0.0125,0.01]) 
#erate= np.array([0.02,0.015,0.0125,0.01]) 



timestep_multiplier=0.05
# estimating number of steps  required
strain=30
delta_t_md=(delta_t_srd/10)*timestep_multiplier
strain_rate= erate
number_steps_needed= np.ceil(strain/(strain_rate*delta_t_md))
dump_freq=10
total_strain_actual=no_timesteps*erate*delta_t_md
#rho=10 
j_=30
rho=5
realisation_index=np.array([1,2,3])
restart_count=0

filepath="/Volumes/Backup Plus 1/PhD_/Rouse Model simulations/Using LAMMPS imac/Simulation_run_folder/hfd5_runs/flat_elastic_tests/test_box_23_M_5_k_10_30"
filepath="/Volumes/Backup Plus 1/PhD_/Rouse Model simulations/Using LAMMPS imac/MYRIAD_LAMMPS_runs/flat_elastic/ensemble_test_30_strain_units"
filepath="/Volumes/Backup Plus 1/PhD_/Rouse Model simulations/Using LAMMPS imac/MYRIAD_LAMMPS_runs/flat_elastic/ensemble_test_30_strain_units_K_60_100"
#filepath="/Volumes/Backup Plus 1/PhD_/Rouse Model simulations/Using LAMMPS imac/MYRIAD_LAMMPS_runs/flat_elastic/ensemble_test_30_strain_K_100_only"

os.chdir(filepath)

#%% loading in arrays to tuple 
stress_tensor_summed_1d_tuple=()
stress_tensor_summed_tuple_shaped=()
area_vector_1d_tuple=()
area_vector_tuple_shaped=()
delta_mom_pos_tensor_summed_1d_tuple=()
delta_mom_pos_tensor_summed_tuple_shaped=()
ke_tensor_summed_1d_tuple=()
ke_tensor_summed_tuple_shaped=()
spring_pos_tensor_summed_1d_tuple=()
spring_pos_tensor_summed_tuple_shaped=()


array_size=((no_timesteps/(dump_freq/timestep_multiplier))).astype('int')

     


for i in range(erate.size):
    cumsum_divsor_array_stress=np.tile(np.repeat(np.array([np.arange(1,array_size[i]+1)]),\
                                         repeats=9, axis=0).T,(internal_stiffness.size,1,1))
    cumsum_divsor_array_ke=np.tile(np.repeat(np.array([np.arange(1,array_size[i]+1)]), \
                                         repeats=6, axis=0).T,(internal_stiffness.size,1,1))
   
    #loading in 
    stress_tensor_summed_1d_tuple=stress_tensor_summed_1d_tuple+\
        (np.load("stress_tensor_summed_1d_test_restartcount_0_erate_"+str(erate[i])+\
        "_bk_10000_K_"+str(internal_stiffness[0])+"_"+str(internal_stiffness[-1])+\
        "_L_"+str(int(box_size))+"_no_timesteps_"+str(no_timesteps[i])+".npy"),)
    delta_mom_pos_tensor_summed_1d_tuple=delta_mom_pos_tensor_summed_1d_tuple+\
        (np.load("delta_mom_pos_tensor_summed_1d_test_restartcount_0_erate_"+\
        str(erate[i])+"_bk_10000_K_"+str(internal_stiffness[0])+"_"+\
        str(internal_stiffness[-1])+"_L_"+str(int(box_size))+"_no_timesteps_"+\
        str(no_timesteps[i])+".npy"),)
    ke_tensor_summed_1d_tuple=ke_tensor_summed_1d_tuple+\
        (np.load("kinetic_energy_tensor_summed_1d_test_restartcount_0_erate_"+\
        str(erate[i])+"_bk_10000_K_"+str(internal_stiffness[0])+"_"+\
        str(internal_stiffness[-1])+"_L_"+str(int(box_size))+"_no_timesteps_"+\
        str(no_timesteps[i])+".npy"),)
    spring_pos_tensor_summed_1d_tuple=spring_pos_tensor_summed_1d_tuple+\
        (np.load("spring_pos_tensor_summed_1d_test_restartcount_0_erate_"+\
        str(erate[i])+"_bk_10000_K_"+str(internal_stiffness[0])+"_"+\
        str(internal_stiffness[-1])+"_L_"+str(int(box_size))+"_no_timesteps_"+\
        str(no_timesteps[i])+".npy"),)
    area_vector_1d_tuple=area_vector_1d_tuple+\
        (np.load("area_vector_summed_1d_test_restartcount_0_erate_"+str(erate[i])+\
        "_bk_10000_K_"+str(internal_stiffness[0])+"_"+str(internal_stiffness[-1])+\
        "_L_"+str(int(box_size))+"_no_timesteps_"+str(no_timesteps[i])+".npy"),)
   
    # reshaping and taking realisation mean , then taking cumulative sum along timestep axis, then dividing by the array of total values 
    stress_tensor_summed_tuple_shaped=stress_tensor_summed_tuple_shaped+\
        (np.cumsum(np.mean\
        (np.reshape(stress_tensor_summed_1d_tuple[i],(internal_stiffness.size,j_,array_size[i],9))\
        ,axis=1),axis=1)/cumsum_divsor_array_stress,)
    delta_mom_pos_tensor_summed_tuple_shaped=delta_mom_pos_tensor_summed_tuple_shaped+\
        (np.cumsum(np.mean\
        (np.reshape(delta_mom_pos_tensor_summed_1d_tuple[i],(internal_stiffness.size,j_,array_size[i],9)),\
        axis=1),axis=1)/cumsum_divsor_array_stress,)
    spring_pos_tensor_summed_tuple_shaped=spring_pos_tensor_summed_tuple_shaped+\
        (np.cumsum(np.mean\
        (np.reshape(spring_pos_tensor_summed_1d_tuple[i],(internal_stiffness.size,j_,array_size[i],9))\
        ,axis=1),axis=1)/cumsum_divsor_array_stress,)
    
    ke_tensor_summed_tuple_shaped=ke_tensor_summed_tuple_shaped+\
        (np.cumsum(np.mean\
        (np.reshape(ke_tensor_summed_1d_tuple[i],(internal_stiffness.size,j_,array_size[i],6)),\
        axis=1),axis=1)/cumsum_divsor_array_ke,)
    area_vector_tuple_shaped=stress_tensor_summed_tuple_shaped+\
        (np.mean\
        (np.reshape(area_vector_1d_tuple[i],(internal_stiffness.size,j_,array_size[i],3)),axis=1),)
    
        

labels_coll=["$\Delta p_{x}r_{x}$","$\Delta p_{y}r_{y}$","$\Delta p_{z}r_{z}$","$\Delta p_{x}r_{z}$","$\Delta p_{x}r_{y}$","$\Delta p_{y}r_{z}$","$\Delta p_{z}r_{x}$","$\Delta p_{y}r_{x}$","$\Delta p_{z}r_{y}$"]
labels_stress=["$\sigma_{xx}$","$\sigma_{yy}$","$\sigma_{zz}$","$\sigma_{xz}$","$\sigma_{xy}$","$\sigma_{yz}$","$\sigma_{zx}$","$\sigma_{zy}$","$\sigma_{yx}$"]
labels_gdot=["$\dot{\gamma}= "]

no_data_sets=internal_stiffness.size



#%% calculating strain x points

strainplot_tuple=()
for i in range(0,erate.shape[0]):
    units_strain=(total_strain_actual[i]/array_size[i])
    strainplot=np.zeros((array_size[i]))
    for j in range(0,array_size[i]):
         strainplot[j]=j*units_strain
    
    strainplot_tuple=strainplot_tuple+(strainplot,)



# mean_step=np.array([9998])


def folder_check_or_create(filepath,folder):
     os.chdir(filepath)
     # combine file name with wd path
     check_path=filepath+"/"+folder
     print((check_path))
     if os.path.exists(check_path) == 1:
          print("file exists, proceed")
          os.chdir(check_path)
     else:
          print("file does not exist, making new directory")
          os.chdir(filepath)
          os.mkdir(folder)
  

     

     
####NOTE could i turn this set of plotting functions into a class?
from whittaker_eilers import WhittakerSmoother        
def use_whittaker_smoother(data_vector,lbda,ord):
    whittaker_smoother = WhittakerSmoother(
    lmbda=lbda, order=ord, data_length=len(data_vector))

    smoothed_data = whittaker_smoother.smooth(data_vector)
    return smoothed_data


 
#%% plotting rolling average diagonal against strain 
folder_normal="normal_stress_plots"
folder_check_or_create(filepath,folder_normal)

#stress_tensor_summed_realisation_mean_rolling_hline=np.mean(stress_tensor_summed_realisation_mean_rolling[:,:,0:3])
labelpady=15
fontsize=15
std_dv_stress=[]
plt.rcParams.update({'font.size': 12})
for k in range(0,erate.size):
#for k in range(1,2):
    for i in range(0,internal_stiffness.size):
    #for i in range(0,1):
    

        for j in range(0,3):

            plt.plot(strainplot_tuple[k], stress_tensor_summed_tuple_shaped[k][i,:,j],label=labels_stress[j],color=colour[j])
          #  smoothed_data=use_whittaker_smoother(stress_tensor_summed_tuple_shaped[k][i,:,j],20000000000000,2)
          #  plt.plot(strainplot_tuple[k][:],smoothed_data,colour[i+3],label="$K="+str(internal_stiffness[i])+"$, smoothed")
            plt.ylabel('$\sigma_{\\alpha \\alpha}$', rotation=0, labelpad=labelpady)
            plt.xlabel("$\gamma$")
            #plt.ylim((10.5,11))

        #plt.axhline(stress_tensor_summed_realisation_mean_rolling_hline,0,1000, label="$\\bar{\sigma_{\\alpha \\alpha}}="+str(sigfig.round(stress_tensor_summed_realisation_mean_rolling_hline,sigfigs=3))+"$",linestyle='dashed',color=colour[6])
        plt.legend(loc='best')
        plt.title("Normal stress $\sigma_{\\alpha \\alpha}$ against strain $\gamma$, $\dot{\gamma}="\
                  +str(erate[k])+"$ and $K="+str(internal_stiffness[i])+"$")
        #plt.tight_layout()
        plt.savefig("rolling_ave_normal_stress_vs_strain_gdot_"+str(erate[k])+"_K_"+str(internal_stiffness[i])+"_M_"+str(rho)+"_L_"+str(box_size)+".pdf",dpi=1200,bbox_inches='tight')
        plt.show()

#%%first normal stress difference rolling vs strain 
folder="normal_stress_difference_plots"
folder_check_or_create(filepath,folder)

labelpady=15
fontsize=15
plt.rcParams.update({'font.size': 12})
for k in range(0,erate.size):
    for i in range(0,internal_stiffness.size):
        #for j in range(0,3):
           
            N_1=stress_tensor_summed_tuple_shaped[k][i,:,0]-stress_tensor_summed_tuple_shaped[k][i,:,2]
           
            plt.plot(strainplot_tuple[k][:],N_1[:],label="$K="+str(internal_stiffness[i])+"$",color=colour[i])#, \\bar{N_{1}}="+str(sigfig.round(N_1_mean,sigfigs=3))+"$",color=colour[i])
            plt.ylabel('$N_{1}$', rotation=0, labelpad=labelpady)
            plt.xlabel("$\gamma$")
            smoothed_data=use_whittaker_smoother(N_1,10000000000000,2)
            plt.plot(strainplot_tuple[k][:],smoothed_data,colour[i+3],label="$K="+str(internal_stiffness[i])+"$, smoothed")
            #plt.ylim((-0.1,5))

    plt.legend(loc='best',bbox_to_anchor=(1,1))
    plt.title("Normal stress difference $N_{1}$ against strain $\gamma$, $\dot{\gamma}="\
                  +str(erate[k])+"$")
        #plt.tight_layout()
    plt.savefig("N_1_vs_strain_gdot_"+str(erate[k])+"_M_"+str(rho)+\
                "_L_"+str(box_size)+".pdf",dpi=1200,bbox_inches='tight')
    plt.show()

#%% N_1 vs shear rate 
    
folder="normal_stress_difference_plots"
folder_check_or_create(filepath,folder)
# take last value as true N_1

N_1_final=np.zeros((internal_stiffness.size,erate.size))
for k in range(0,erate.size):
    for i in range(0,internal_stiffness.size):
          N_1_final[i,k]=stress_tensor_summed_tuple_shaped[k][i,-1,0]-stress_tensor_summed_tuple_shaped[k][i,-1,2]
           

labelpady=15
fontsize=15
plt.rcParams.update({'font.size': 12})

for i in range(0,internal_stiffness.size):
        #for j in range(0,3):
    plt.plot(erate[:],N_1_final[i,:],label="$K="+str(internal_stiffness[i])+"$",color=colour[i],marker="x")#, \\bar{N_{1}}="+str(sigfig.round(N_1_mean,sigfigs=3))+"$",color=colour[i])
    
    plt.ylabel('$N_{1}$', rotation=0, labelpad=labelpady)
    plt.xlabel("$\dot{\gamma}$")
        
        #plt.ylim((-0.1,5))

    plt.legend(loc='best',bbox_to_anchor=(1,1))
    plt.title("Normal stress difference $N_{1}$ against shear rate $\dot{\gamma}$")
        #plt.tight_layout()
    plt.savefig("N_1_vs_shearrate_M_"+str(rho)+\
                "_L_"+str(box_size)+".pdf",dpi=1200,bbox_inches='tight')
plt.show()
    


#%% second normal vs strain 
folder="second_normal_stress_difference_plots"
folder_check_or_create(filepath,folder)
labelpady=15
fontsize=15
plt.rcParams.update({'font.size': 12})
for k in range(0,erate.size):
    for i in range(0,internal_stiffness.size):
    #for j in range(0,3):
        N_2=stress_tensor_summed_tuple_shaped[k][i,:,2]-stress_tensor_summed_tuple_shaped[k][i,:,1]
        #N_2_mean=np.mean(N_2[mean_step[0]:])
        plt.plot(strainplot_tuple[k][:],N_2[:],label="$K="+str(internal_stiffness[i])+"$")#, \\bar{N_{2}}="+str(sigfig.round(N_2_mean,sigfigs=3))+"$",color=colour[i])
        smoothed_data=use_whittaker_smoother(N_2,2000000000000,2)
        plt.plot(strainplot_tuple[k][:],smoothed_data,colour[i+5],label="$K="+str(internal_stiffness[i])+"$, smoothed")
       
        plt.ylabel('$N_{2}$', rotation=0, labelpad=labelpady)
        plt.xlabel("$\gamma$")
        #plt.ylim((-0.1,0.1))

    plt.legend(loc='best',bbox_to_anchor=(1,1))
    plt.title("Normal stress difference $N_{2}$ against strain $\gamma$, $\dot{\gamma}="\
                  +str(erate[k])+"$")
    #plt.tight_layout()
    plt.savefig("N_2_strain_gdot_"+str(erate[k])+"_M_"+str(rho)+\
                "_L_"+str(box_size)+".pdf",dpi=1200,bbox_inches='tight')
    plt.show()

#%% N_2 vs shear rate 
    
folder="second_normal_stress_difference_plots"
folder_check_or_create(filepath,folder)
# take last value as true N_1

N_2_final=np.zeros((internal_stiffness.size,erate.size))
for k in range(0,erate.size):
    for i in range(0,internal_stiffness.size):
          N_2_final[i,k]=stress_tensor_summed_tuple_shaped[k][i,-1,2]-stress_tensor_summed_tuple_shaped[k][i,-1,1]
           

labelpady=15
fontsize=15
plt.rcParams.update({'font.size': 12})

for i in range(0,internal_stiffness.size):
        #for j in range(0,3):
    plt.plot(erate[:],N_2_final[i,:],label="$K="+str(internal_stiffness[i])+"$",color=colour[i])#, \\bar{N_{1}}="+str(sigfig.round(N_1_mean,sigfigs=3))+"$",color=colour[i])
    plt.ylabel('$N_{2}$', rotation=0, labelpad=labelpady)
    plt.xlabel("$\dot{\gamma}$")
        
        #plt.ylim((-0.1,5))

    plt.legend(loc='best',bbox_to_anchor=(1,1))
    plt.title("Normal stress difference $N_{2}$ against shear rate $\dot{\gamma}$")
        #plt.tight_layout()
    plt.savefig("N_2_vs_shearrate_M_"+str(rho)+\
                "_L_"+str(box_size)+".pdf",dpi=1200,bbox_inches='tight')
plt.show()


#%% plotting xz component vs strain 
folder="shear_stress_plots"
folder_check_or_create(filepath,folder)
labelpady=10
fontsize=15
plt.rcParams.update({'font.size': 12})
for k in range(0,erate.size):
    for i in range(0,internal_stiffness.size):
        for j in range(3,4):
            #stress_tensor_summed_realisation_mean_rolling_hline=np.mean(stress_tensor_summed_realisation_mean_rolling[i,mean_step:,3])
            plt.plot(strainplot_tuple[k][:],stress_tensor_summed_tuple_shaped[k][i,:,j],label="$K="+str(internal_stiffness[i])+"$",color=colour[i])
            smoothed_data=use_whittaker_smoother(stress_tensor_summed_tuple_shaped[k][i,:,j],5000000000000,2)
            plt.plot(strainplot_tuple[k][:],smoothed_data,colour[i+5],label="$K="+str(internal_stiffness[i])+"$, smoothed")
       
            plt.ylabel('$\sigma_{xz}$', rotation=0, labelpad=labelpady)
            plt.xlabel("$\gamma$")
    #plt.ylim((0,0.01))
       
    plt.legend()
    plt.title("Shear stress $\sigma_{xz}$ against strain $\gamma$, $\dot{\gamma}="\
                  +str(erate[k])+"$")
    plt.savefig("rolling_ave_shear_stress_vs_strain_gdot_"+str(erate[k])+"_K_"+str(internal_stiffness[i])+\
                "_M_"+str(rho)+"_L_"+str(box_size)+".pdf",dpi=1200,bbox_inches='tight')

        #plt.tight_layout()
        #plt.savefig("rolling_ave_shear_stress_tensor_elements_xy_gdot_allgdot_M_"+str(rho)+"_L_"+str(box_size)+".png",dpi=1200)
        #plt.savefig("rolling_ave_shear_stress_tensor_vs_strain_elements_xy_gdot_M_"+str(rho)+"_L_"+str(box_size)+".png",dpi=1200)
    plt.show()


#%% plotting whole off diagonal of stress tensor apart from shearing plane
folder="shear_stress_non_shear_plane_plots"
folder_check_or_create(filepath,folder)    
labelpady=15
fontsize=15
plt.rcParams.update({'font.size': 12})
for k in range(0,erate.size):
    for i in range(0,internal_stiffness.size):
        for j in range(4,6):
            #stress_tensor_summed_realisation_mean_rolling_hline=np.mean(stress_tensor_summed_realisation_mean_rolling[i,mean_step:,3])
            plt.plot(strainplot_tuple[k][:],stress_tensor_summed_tuple_shaped[k][i,:,j],label=labels_stress[j],color=colour[j])
            smoothed_data=use_whittaker_smoother(stress_tensor_summed_tuple_shaped[k][i,:,j],5000000000000,2)
            plt.plot(strainplot_tuple[k][:],smoothed_data,colour[i+1],label="$K="+str(internal_stiffness[i])+"$, smoothed")
       
            plt.ylabel('$\sigma_{\\alpha \\beta}$', rotation=0, labelpad=labelpady)
            plt.xlabel("$\gamma$")
        # plt.ylim((0,1))
            
       
        plt.title("Shear stress $\sigma_{\\alpha \\beta}, \\alpha \\beta \\neq xz $ against strain $\gamma$, $\dot{\gamma}="\
                  +str(erate[k])+"$")
        plt.legend()
        plt.savefig("rolling_ave_shear_stress_nonshearplane_vs_strain_gdot_"+str(erate[k])+"_K_"+str(internal_stiffness[i])+\
                "_M_"+str(rho)+"_L_"+str(box_size)+".pdf",dpi=1200,bbox_inches='tight')
        plt.show()

#%% area vector convert to spherical  
bin_count = int(np.ceil(np.log2((j_))) + 1)# sturges rule


# I think this is only looking at one shear rate at a time 
folder="theta_and_phi_histograms"
folder_check_or_create(filepath,folder)  
for i in range(erate.size):
    
        spherical_coordinates_area_vector=np.zeros((internal_stiffness.size,array_size[i],3))
        x=area_vector_tuple_shaped[i][:,:,0]
        y=area_vector_tuple_shaped[i][:,:,1]
        z=area_vector_tuple_shaped[i][:,:,2]
        for l in range(internal_stiffness.size):
            for j in range(z.shape[1]):
                if z[l,j]<0:
                    z[l,j]=-1*z[l,j]
                    y[l,j]=-1*y[l,j]
                    x[l,j]=-1*x[l,j]

                else:
                    continue

        # radial coord
        spherical_coordinates_area_vector[:,:,0]=np.sqrt((x**2)+(y**2)+(z**2))
        # theta coord 
        spherical_coordinates_area_vector[:,:,1]=np.sign(y)*np.arccos(x/(np.sqrt((x**2)+(y**2))))
        # phi coord
        spherical_coordinates_area_vector[:,:,2]=np.arccos(z/spherical_coordinates_area_vector[:,:,0])


   
        for k in range(internal_stiffness.size):
                # plot theta histogram
                pi_theta_ticks=[ -np.pi, -np.pi/2, 0, np.pi/2,np.pi]
                pi_theta_tick_labels=['-π','-π/2','0', 'π/2', 'π'] 
                plt.hist((spherical_coordinates_area_vector[k,:,1]))
                plt.xticks(pi_theta_ticks, pi_theta_tick_labels)
                plt.title("Azimuthal angle $\Theta$ histogram,$\dot{\gamma}="\
                  +str(erate[i])+"$ and $K="+str(internal_stiffness[k])+"$")
                plt.xlabel('$\\theta$')
                plt.tight_layout()
                plt.savefig("theta_histogram_"+str(j_)+"_points_erate_"+str(erate[i])+"_K_"+str(internal_stiffness[k])+".pdf",dpi=1200)
                plt.show()


                pi_phi_ticks=[ 0,np.pi/4, np.pi/2,3*np.pi/4,np.pi]
                pi_phi_tick_labels=[ '0','π/4', 'π/2','3π/4' ,'π']
                frequencies_phi= np.histogram(spherical_coordinates_area_vector[:,2],bins=bin_count)[0]


                # plot phi hist

                plt.hist(spherical_coordinates_area_vector[k,:,2])
                plt.xticks(pi_phi_ticks,pi_phi_tick_labels)
                plt.xlabel('$\phi$')
                plt.title("Inclination angle $\phi$ histogram,$\dot{\gamma}="\
                  +str(erate[i])+"$ and $K="+str(internal_stiffness[k])+"$")
                plt.tight_layout()
                plt.savefig("phi_histogram_"+str(j_)+"_points_erate_"+str(erate[i])+"_K_"+str(internal_stiffness[k])+".pdf",dpi=1200)
                plt.show()

# would be nice to see the all the data for each spring stiffness
#%% viscosity estimate
#stress_tensor_summed_realisation_mean_rolling_hline=np.mean(stress_tensor_summed_realisation_mean_rolling[:,mean_step:,3],axis=1)

alpha=np.pi
dim=3
def collisional_visc(alpha,rho,dim):
    coll_visc= (1/(6*dim*rho))*(rho-1+np.exp(-rho))*(1-np.cos(alpha))
    return coll_visc
def kinetic_visc(alpha,rho):
    kin_visc= (5*rho)/((rho-1+np.exp(-rho))*(2-np.cos(alpha)-np.cos(2*alpha)))  -1 
    return kin_visc

total_kinematic_visc= kinetic_visc(alpha,rho) + collisional_visc(alpha,rho,dim)
shear_dynamic_visc_prediction= total_kinematic_visc*rho

#%% stress vs strain rate plot 
viscosity=np.zeros((erate.size))
stress_tensor_summed_mean=np.zeros((internal_stiffness.size,erate.size))
for k in range(0,internal_stiffness.size):
    for i in range(4):
     stress_tensor_summed_mean[k,i]=stress_tensor_summed_tuple_shaped[i][k,-1,3]
#    viscosity[i]=stress_tensor_summed_mean[i]/erate[i]


#%% 
folder="shear_stress_vs_strain_plot"
folder_check_or_create(filepath,folder)  
for k in range(0,internal_stiffness.size):
    fit=np.polyfit(erate,stress_tensor_summed_mean[k,:],1)
    plt.scatter(erate, stress_tensor_summed_mean[k,:])
    #plt.axhline(np.mean(stress_tensor_summed_mean[k,:]))

    plt.plot(erate,fit[0]*erate + fit[1], label="$K="+str(internal_stiffness[k])+"$ & $\\frac{d \sigma_{xz}}{d \dot{\gamma}}="+str(sigfig.round(fit[0],sigfigs=3))+"$")
    plt.xticks(erate) 
    plt.xlabel("$\dot{\gamma}$",rotation=0)
    #plt.ylim((0.0003,0.0005))
    plt.ylabel("$\sigma_{xz}$",rotation=0,labelpad=labelpady)
    plt.legend(loc='upper right',bbox_to_anchor=(1.6,1))
    #plt.tight_layout()
plt.savefig("shear_stress_vs_shear_rate_gdot_"+str(erate[0])+"_"+str(erate[-1])+"_M"+str(rho)+"_L_"+str(box_size)+".png",dpi=1200)
plt.show()



# %%
