#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 09:22:57 2018

@author: earkpr
"""


import iris
import matplotlib.pyplot as plt
import os
import numpy.ma as ma
import numpy as np

import sys
#%%


path_to_observations = '/nfs/a201/earkpr/Jo_Comparison_to_Observations/Interpolate/'
data_out = "/nfs/a201/earkpr/Jo_Comparison_to_Observations/Python_Comp_to_Obs/UKCA_postproc/Data_Out/"

os.listdir(path_to_observations)

orog_file = "n96_hadgem1_qrparm.orog_new.pp"
iris.load(orog_file)



# Jo's data needs transposed to fit with model N96 and needs coordinate details added.

# Read in an example model file (for coordinates)
example_file = '/nfs/a201/earkpr/Jo_Comparison_to_Observations/Model_Data/L1_Ntot_Total_particle_concentration.nc'
#example_N48_file = "/nfs/a201/earkpr/DataVisualisation/GASSP/N48_Lon_Lat_Grid.nc"
example_N48_file = "aod550_total_teafw_pm2008jan_N48_dim_att_j.nc"


#obs_cubes_number =  iris.load(path_to_observations+"N96ND_mm_Nx_arrays.nc",orog_file)
#print(obs_cubes_number)

#obs_cubes_number =  iris.load('/nfs/a201/earkpr/Jo_Comparison_to_Observations/Interpolate/N96ND_mm_Nx_arrays.nc')
#obs_cubes_bc = iris.load(path_to_observations+"N96ND_BC_data_from_AEROCOM_arrays.nc",orog_file)
#obs_cubes_pm = iris.load(path_to_observations+"N96ND_mm_PM2pt5_arrays.nc",orog_file)
#obs_cubes_mask = iris.load(path_to_observations+"N96ND_mask_arrays.nc",orog_file)

unit_conversion = ['1e6','1e6','1e6','1e0']
months = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
    
dict = {'Ntot': 'Ntot', 'N100': 'N100', 'N50': 'N50', 'PM25':'PM25','bc_vertical load':'BC_LOAD'}

dict_unit_convert = { 'Ntot': 1E6,
                      'N100': 1E6, 
                      'N50' : 1E6, 
                    'PM2pt5': 1E0,
                   'BC_mass': 1E0
                     }

example_cube = iris.load(example_file)
example_N48_cube_large = iris.load(example_N48_file)
example_N48_cube_latlon = example_N48_cube_large[0][0,0,:,:]

print(example_N48_cube_latlon)

file_list = ["N96ND_mm_Nx_arrays.nc","N96ND_BC_data_from_AEROCOM_arrays.nc","N96ND_mm_PM2pt5_arrays.nc","N96ND_mask_arrays.nc"]

variable_long_name = ['Ntot','N50','N100','PM2pt5']

obs_cube_list = ['obs_cubes_number', 'obs_cubes_bc', 'obs_cubes_pm', 'obs_cubes_mask']


for file in file_list:

    print("file = ",file)

    obs_cubes = iris.load(path_to_observations+file)

    print(path_to_observations+str(file))
    print("obs_cubes = ",obs_cubes)
                    
    for imonth, month in enumerate(months[1:]):

        print('imonth = ',imonth, month)


        for cube in obs_cubes:

            print("cube = ",cube)
            print("cube.long_name = ",cube.long_name)
            print("cube.var_name = ",cube.var_name)

            if str(cube.var_name) in variable_long_name:

                print("UNITS ")
                print(dict_unit_convert[cube.var_name])

                #transpose obs data to sams shape as model.          
                obs_data_temp = np.nan_to_num(cube.data)
                obs_data_transposed = obs_data_temp.transpose([3,0,1,2])
                        
                # Convert units of observations, if required
                print( "Unit conversion = ",dict_unit_convert[cube.var_name])
                obs_data_transposed = obs_data_transposed * float(dict_unit_convert[cube.var_name]) 
    
                #print('example_cube')
                #print(example_cube[0])
                #print(example_cube)
        
                ## Put Jo's obs data in a cube like the model data (to get correct coords)           
                ## (Not regridding, just taking the coordinate labelling and transposing)
                test_temp = example_cube[0][imonth]
                obs_data_cube = test_temp
                obs_data_cube.data = obs_data_transposed[imonth,:,:,:]
                obs_data_cube.var_name = cube.var_name 
                obs_data_cube.long_name = cube.long_name 
                    
                print (obs_data_cube)
                    
                # Average in the vertical to get 1D data
                vertical_mean = obs_data_cube.collapsed('model_level_number', iris.analysis.MEAN)
           
                #print(np.max(vertical_mean.data), np.mean(vertical_mean.data), np.min(vertical_mean.data))
    
                #print(vertical_mean)
                    
                # Write out data at N96                                  
                file_out = str(data_out)+"N96_Data_"+str(months[imonth])+"_Jo_obs_verticallyaveraged_data.nc"
                cube_list = [vertical_mean]
                iris.save(cube_list,str(file_out)) 
           
                vertical_mean_small = vertical_mean[:,:]
                    
                # Write out data at N96                                  
                file_out = str(data_out)+"N96_TESTING_data.nc"
                cube_list = [vertical_mean, example_N48_cube_latlon, vertical_mean_small]
                iris.save(cube_list,str(file_out)) 
                
                    
                for coord in example_N48_cube_latlon.coords():
                    print(coord.name())
                print("")
                    
                #  Regrid to N48
                vertical_mean_regrid = vertical_mean.regrid(example_N48_cube_latlon, iris.analysis.Linear())
                vertical_mean_regrid.long_name = vertical_mean_regrid.long_name + 'regridded to N48'
    
                print("example_N48_cube_latlon")
                print(example_N48_cube_latlon)
                print("vertical_mean_regrid")
                print(vertical_mean_regrid)
                print("vertical_mean")
                print(vertical_mean)
    
                cube_list = [vertical_mean_regrid,vertical_mean]
                iris.save(cube_list,"/nfs/a201/earkpr/DataVisualisation/GASSP/Files_For_Jill/N48_Data_"+str(months[imonth])+"_Jo_obs_verticallyaveraged_"+str(cube.var_name)+".nc")

#%%
