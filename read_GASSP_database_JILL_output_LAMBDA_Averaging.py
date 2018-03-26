# -*- coding: utf-8 -*-

# K. Pringle
#
# Code to convert GASSP Level 2 data onto a destination gridded netCDF grid.
# Code will also create average of a single month (e.g. July) over multiple years.

#!/usr/bin/python2.7


import iris
import numpy as np
import sys
import datetime
from iris.time import PartialDateTime

iris.FUTURE.netcdf_no_unlimited=True

import iris.coord_categorisation
import datetime
import iris.unit
import cf_units
import numpy.ma as ma
import os
import re


# python ≥3.0

def only_numerics(seq):
    numeric_values= re.sub('[a-zA-Z]','',seq)
    return numeric_values


#%%

# User settings
# variable_name = 'PM2P5'
# variable_long_name = 'PM2P5_Concentrations_from_GASSP_on_N48_grid'
#variable_name = 'SO4'
#variable_long_name = 'SO4_Concentrations_from_GASSP_on_N48_grid'

start_year = 2005
final_year = 2010
month_to_average = 'Jul'  #  Need to use IRIS month naming convention.  Three letter month name


#variable_names = ['SO4','ORG','PM2P5']
#variable_long_names = ['SO4_Concentrations_from_GASSP_on_N48_grid','ORG_Concentrations_from_GASSP_on_N48_grid','PM2P5_Concentrations_from_GASSP_on_N48_grid']

variable_names = ['ORG']
variable_long_names = ['ORG_Concentrations_from_GASSP_on_N48_grid']

#variable_names = ['PM2P5']
#variable_long_names = ['PM2P5_Concentrations_from_GASSP_on_N48_grid']

# Dictionary of alternative variable names
dict_of_variable_names_PM2P5 = {"PM2P5":"PM2P5"}
dict_of_variable_names_SO4 = {"SO4":"SO4","Sulfate":"SO4","Sulphate":"SO4","S04":"SO4","particulate sulfate":"SO4"}
dict_of_variable_names_ORG = {"ORG":"ORG","Organic":"ORG","AMS mass concentration of Org":"ORG"}


for idx, variable_name in enumerate(variable_names):
    
    if (variable_name  == "SO4"):
        dict_of_variable_names = dict_of_variable_names_SO4
    if (variable_name  == "ORG"):
        dict_of_variable_names = dict_of_variable_names_ORG
    if (variable_name  == "PM2P5"):
        dict_of_variable_names = dict_of_variable_names_PM2P5

    try:
        print(dict_of_variable_names)
    except:
        print("WARNING:  No dictionary defined")

    variable_long_name = variable_long_names[idx]

    # Location of GASSP data
    path = '/nfs/a201/earkpr/DataVisualisation/GASSP/GASSP_Level_2_Data/'
    #path = '/nfs/a201/earkpr/DataVisualisation/GASSP/Nigel_Code/Level2/IMPROVE/'

#%%

    #  Read in file on destination grid

    file_destination = "/nfs/a201/earkpr/DataVisualisation/GASSP/N48_Lon_Lat_Grid.nc"
    cube_destination = iris.load(file_destination)


    #  Just take a lat / lon grid (ignore realization, time and hybrid_ht)
    test_temp = cube_destination[0]
    test = test_temp[0, 0, 0, :, :]

    cube_dest = test

    cube_destination_empty = cube_dest.copy()
    cube_destination_empty.data[:,:] = np.nan
    cube_destination_empty.long_name = str(variable_long_name)
    cube_destination_empty.var_name = str(variable_name) 
    #print(cube_destination_empty.data)

    cube_average_count = cube_dest.copy()
    cube_average_count.data[:,:] = 0.0
    #print(cube_average_count.data)
    cube_average_count.long_name = "Array to count number of stations contributing to the data"
    cube_average_count.var_name = "observations_counter"


    #iris.save(cube_destination_empty, "/nfs/a201/earkpr/DataVisualisation/GASSP/Destination_netCDF.nc")


    #%%

    ncfiles = []
    for root, dirs, files in os.walk(str(path)):
    #for root, dirs, files in os.walk('/nfs/a201/earkpr/DataVisualisation/GASSP/'):
      for file in files: 
        if file.endswith('.nc'):
            if str(variable_name) in file:    
##               if str("Ba") in file:
                 if str("Station") or str("Ship") in file:           
#                 if str("Station") in file:           
#                     if str("Ship") in file:           
##                     if str("B") in file:           
                     ncfiles.append(os.path.join(root, file))
                   
#%%               
    #print(path)            
    #print(ncfiles)

    #%% 

    # Read all cubes in list 
    #cube_list = iris.load(ncfiles)

    #print(cube_list)

    for file in ncfiles:

        cubes = iris.load(file)

        station_lat_array = []
        station_lon_array = []

        # Ship data has lat lon as a cube 
        if str("Ship") in file:

            for cube in cubes:
                if(cube.var_name.upper() == 'LATITUDE'):
                    #print("Latitude = ",cube.data)
                    station_lat_array = cube.data
                if(cube.var_name.upper() == 'LONGITUDE'):
                    #print("Lon = ",cube.data)
                    station_lon_array = cube.data

            #print("")
            #print("station_lon_array = ",station_lon_array)
            #print("station_lat_array = ",station_lat_array)


        if str("Station") in file:    

            for cube in cubes:
                #if(cube.var_name == str(variable_name)):
                #print("dict keys  = ",dict_of_variable_names.keys())
                #print("dict values  = ",dict_of_variable_names.values())

                if(cube.var_name in dict_of_variable_names.keys()):

                    try:
                        #  Remove the N and E and degN and degE characters from lat / lon string
                        cube.attributes['Station_Lon'] = only_numerics(cube.attributes['Station_Lon'])
                        cube.attributes['Station_Lat'] = only_numerics(cube.attributes['Station_Lat'])
                        #print("LON =",cube.attributes['Station_Lon']," LAT = ",cube.attributes['Station_Lat'])
                    except:
                        print("WARNING:  Station data cube has no Station_Lon / Station_Lat attribute")
                    
                    station_lon_array.append(float(cube.attributes['Station_Lon']))
                    station_lat_array.append(float(cube.attributes['Station_Lat']))
    
                    # Convert lon from -180 to 180 to 0 to 360    
                    #print("station_lon_array = ", station_lon_array)
                    #print("station_lat_array = ", station_lat_array)
                    #print("")

        #Correct any data not on 0 to 360 longitude
        #if(float(cube.attributes['Station_Lon']) < 0 ):
        #    cube.attributes['Station_Lon'] = 360.0 + float(cube.attributes['Station_Lon']) 

        station_lon_array = np.array(station_lon_array, dtype=np.float32)
        station_lat_array = np.array(station_lat_array, dtype=np.float32)

        x = np.where(station_lon_array < 0.0)
        try: 
            station_lon_array[x] = 360.0 + station_lon_array[x] 
        except:
            print("No negative longitudes")

            
        # Convert any data from ng m-3 to ug m-3
        #print(cube.units)
        if(cube.units == "ng m-3"):
            cube.convert_units('ug m-3')
            #print(cube.units)
            #print("")


        # Define new time axis
        new_time_unit = iris.unit.Unit('seconds since 1970-01-01 00:00:00', calendar='gregorian')
    
        final_cube_list=[]
    
        for  cube in cubes:

            if(cube.var_name in dict_of_variable_names.keys()):

                for coord in cube.coords():
    
                    # No longer needed as fixed GASSP data time label.
                    if(coord.long_name == 'Time in seconds'):
                        coord.convert_units(new_time_unit)
    
                    if(coord.long_name == 'Time in seconds'):
                        iris.coord_categorisation.add_year(cube, 'Time in seconds',  name='year')
                        iris.coord_categorisation.add_month(cube, 'Time in seconds',  name='month')
                        iris.coord_categorisation.add_month_number(cube, 'Time in seconds' , name='month_number')
    
                # Select data that is between start_year to  final_year  (cube_recent_year)
                year_constraint = iris.Constraint(year=lambda cell: start_year-1 < cell < final_year+1)
                
                cube_recent_year = cube.extract(year_constraint)
    
                #print(" cube_recent_year = ", cube_recent_year)
    
                if(cube_recent_year):
    
                    # Average from time frequency to monthly mean 
                    try:
                        cube_monthly_recent_year = cube_recent_year.aggregated_by(['month'], iris.analysis.MEAN)
                        month_slice = cube_monthly_recent_year.extract(iris.Constraint(month=str(month_to_average)))
      
                        if(isinstance(month_slice, iris.cube.Cube)):
        	                final_cube_list.append(month_slice)
                        else:
                            print("NOT A CUBE")
                    except:
                        print(cube_recent_year)
    
            #print("final_cube_list loop")
            #print(final_cube_list)

            for cube in final_cube_list:

                for iobs in range(len(station_lon_array)):

                    #print("lat = ",station_lat_array[iobs]," lon = ",station_lat_array[iobs])

                    # Find lat / lon of the observation.  For N48
                    index_lat = int((float(station_lat_array[iobs]) + 90.0) / float(2.5))
                    index_lon = int((float(station_lon_array[iobs]) / float(3.75)))

                    if(np.isnan(cube_destination_empty.data[index_lat,index_lon])):    #If NaN then no previous obs data in this gridbox
        
                        cube_destination_empty.data[index_lat,index_lon] = float(cube.data)
                        cube_average_count.data[index_lat,index_lon] = cube_average_count.data[index_lat,index_lon] + 1.0
    
                    else:
                        
                        cube_destination_empty.data[index_lat,index_lon] = float(cube.data)
                        ##cube_destination_empty.data[index_lat,index_lon] = cube_destination_empty.data[index_lat,index_lon] + float(cube.data)
                        cube_average_count.data[index_lat,index_lon] = cube_average_count.data[index_lat,index_lon] + 1.0
    
        # Average data in locations with more than one observation.
       ## cube_destination_empty.data = cube_destination_empty.data / cube_average_count.data 
    
    cube_list = [cube_destination_empty, cube_average_count]
    
    iris.save(cube_list,"/nfs/a201/earkpr/DataVisualisation/GASSP/"+str(variable_name)+"_Concentration_"+str(start_year)+"_"+str(final_year)+"_"+str(month_to_average)+"_LAMBDA_AVERAGED_SHIP_Savemoved.nc", netcdf_format='NETCDF3_CLASSIC')
#            

sys.exit()






























