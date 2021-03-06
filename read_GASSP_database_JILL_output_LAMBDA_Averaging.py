# -*- coding: utf-8 -*-

# K. Pringle
#
# Code to convert GASSP Level 2 data onto a destination gridded netCDF grid.
# Code will also create average of a single month (e.g. July) over multiple years.fi

#!/usr/bin/python2.7
#########!/usr/bin/python3.6


import iris
import numpy as np
import sys
from iris.time import PartialDateTime

iris.FUTURE.netcdf_no_unlimited=True

import iris.coord_categorisation
import datetime
import iris.unit
import cf_units
import numpy.ma as ma
import math
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

##iSORPES = True
iSORPES = False  #  SORPES data processed seperately for Jill

start_year = 2005
final_year = 2015

if iSORPES:
    start_year = 2005
    final_year = 2015

##month_to_average = 'Jul'  #  Need to use IRIS month naming convention.  Three letter month name

months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
##months = ['Nov']

for imonth in range(len(months)):
    month_to_average = str(months[imonth])
  
    #variable_names = ['SO4','ORG','PM2P5']
    #variable_long_names = ['SO4_Concentrations_from_GASSP_on_N48_grid','ORG_Concentrations_from_GASSP_on_N48_grid','PM2P5_Concentrations_from_GASSP_on_N48_grid']
    
    #variable_names = ['SO4']
    #variable_long_names = ['SO4_Concentrations_from_GASSP_on_N48_grid']
        
    #variable_names = ['PM2P5']
    #variable_long_names = ['PM2P5_Concentrations_from_GASSP_on_N48_grid']
    
    variable_names = ['ORG']
    variable_long_names = ['ORG_Concentrations_from_GASSP_on_N48_grid']
    
    #variable_names = ['NUM']
    #variable_long_names = ['N50_Concentrations_from_GASSP_on_N48_grid']
    
    # Dictionary of alternative variable names
    
    dict_of_variable_names_N50 = {"N50":"N50","NUM":"N50","Total number of particles>50nm":"N50"}
    dict_of_variable_names_PM2P5 = {"PM2P5":"PM2P5","PM2p5":"PM2P5","pm2p5":"PM2P5"}
    dict_of_variable_names_SO4 = {"SO4":"SO4","Sulfate":"SO4","Sulphate":"SO4","S04":"SO4","particulate sulfate":"SO4","so4":"SO4","qc_sulfate":"SO4"}
    dict_of_variable_names_ORG = {"ORG":"ORG","Organic":"ORG","AMS mass concentration of Org":"ORG","org":"ORG"}
           
    
    for idx, variable_name in enumerate(variable_names):
        
        if (variable_name  == "SO4"):
            dict_of_variable_names = dict_of_variable_names_SO4
        if (variable_name  == "ORG"):
            dict_of_variable_names = dict_of_variable_names_ORG
        if (variable_name  == "PM2P5"):
            dict_of_variable_names = dict_of_variable_names_PM2P5
        if (variable_name  == "NUM"):
            dict_of_variable_names = dict_of_variable_names_N50
    
        try:
            print(dict_of_variable_names)
        except:
            print("WARNING:  No dictionary defined")
    
        variable_long_name = variable_long_names[idx]
    
        # Location of GASSP data
        # path = '/nfs/a201/libclsr/GASSP/Level_2/'
        
        # KP_Nov_2018 : testing old data path to understand differences between current and Jills version
        path = '/nfs/a201/earkpr/DataVisualisation/GASSP/Nigel_Code/Level2/'
        
        #  path = '/nfs/a201/earkpr/DataVisualisation/GASSP/GASSP_Level_2_Data/'
        # path = '/nfs/a201/earkpr/DataVisualisation/GASSP/Nigel_Code/Level2/IMPROVE/'
    
    
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
    
        ncfiles = []
        for root, dirs, files in os.walk(str(path)):
        #for root, dirs, files in os.walk('/nfs/a201/earkpr/DataVisualisation/GASSP/'):
          for file in files: 
            if file.endswith('.nc'):
                if str(variable_name) in file:    
                    
                     if (str('Station') in file) or (str('Ship') in file):                           
                         
                         if iSORPES:
                             if str('SORPES') in file:                   
                                 print("Processing SORPES data ")
                                 ncfiles.append(os.path.join(root, file))
                                 print("ncfiles = ",ncfiles)
                         else:
                             ##if str('Melpitz_2008-09-15') in file:                   
                             ncfiles.append(os.path.join(root, file))
                                 
                                 
                      ## print("AAA file = ",file)
#                      if str('Ship') in file:                           
#                         if str('SORPES') in file:                           
#                             print("BBB file = ",file)
                         
                         
    
        print("")
        print("ncfiles = ",ncfiles)
        print("")
        print("")
        print("")
       
#    
        for file in ncfiles:
            #print("file = ",file)
    
            cubes = iris.load(file)
            
            # Some data, particularly OC data has negative values.  Set these to np.nan.
            
            #for cube in cubes:
            #    print("mimimum value = ",np.nanmin(cube.data))
            #    cube.data[cube.data < 0] 4= np.NaN
    
            #for cube in cubes:
            #   print("var_name = ",cube.var_name)
    
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
    #                if(cube.var_name == str(variable_name)):
    #                    print("dict keys  = ",dict_of_variable_names.keys())
    #                    print("dict values  = ",dict_of_variable_names.values())
    
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
    
                
            # Define new time axis
            new_time_unit = iris.unit.Unit('seconds since 1970-01-01 00:00:00', calendar='gregorian')
        
            final_cube_list=[]
        
            #print("cubes = ",cubes)
    
            for cube in cubes:
                print("cube loop")
                print("cube.var_name=",cube.var_name,"dict_of_variable_names.keys()",dict_of_variable_names.keys())
    
                if(cube.var_name in dict_of_variable_names.keys()):
                    print("NAME IN DICT OF VARIABLE NAMES")
                    print("file = ",file)
                    print(cube.var_name)
                    print("")
                    
                    # Set any negative values to np.NaN
                    #print("min bef = ",np.nanmin(cube.data))
                    cube.data[cube.data < 0.0] = np.NAN                   
                    cube.data = ma.masked_invalid(cube.data)

                    #print("min aft = ",np.nanmin(cube.data))
                    #print("")                  
    
                    # Convert any data from ng m-3 to ug m-3
                    #print("cube.units")
                    #print(cube.units)
    
                    if(cube.units == "ng m-3"):
                        cube.convert_units('ug m-3')
                        print(cube.units)
                        print("")
    
                    for coord in cube.coords():
                        #print("coord = ",coord)
        
                        # No longer needed as fixed GASSP data time label.
                        if(coord.long_name == 'Time in seconds'):
                            coord.convert_units(new_time_unit)
        
                        if(coord.long_name == 'Time in seconds'):

                            #print("Time in seconds")
                                                      
                            if iSORPES:
                                # Works for SORPES but not other data.
                                iris.coord_categorisation.add_year(cube, 'time',  name='year')
                                iris.coord_categorisation.add_month(cube, 'time',  name='month')
                                iris.coord_categorisation.add_month_number(cube, 'time' , name='month_number')
                                
                            else:       # if iSORPES is False                                                 
                                try:                       
                                    iris.coord_categorisation.add_year(cube, 'Time in seconds',  name='year')                             
                                except Exception:
                                    print("Failed to add year coordinate")
                                    pass
                                    #sys.exit()
    
                                try:                            
                                    iris.coord_categorisation.add_month(cube, 'Time in seconds',  name='month')
                                    
                                except Exception:
                                    print("Failed to add month coordinate")
                                    pass
                                    #sys.exit()                            
                                    
                                try:    
                                    iris.coord_categorisation.add_month_number(cube, 'Time in seconds' , name='month_number')
                                except Exception:
                                    print("Failed to add month_number coordinate")
                                    pass
                            #    # sys.exit()                            
        
                    #print(cube)
                    #print("After adding coord_categorisation.add_year ect" )
                    
                    #print(start_year)
                    #print(final_year)

                    #for coord in cube.coords():
                    #    print(coord.name())
                    #    print(coord)
                    #    
                        
                    # Select data that is between start_year to  final_year  (cube_recent_year)
                    year_constraint = iris.Constraint(year=lambda cell: start_year-1 < cell < final_year+1)

                    #print("year_constraint",year_constraint)

                    #print("After year constraint " )
                    cube_recent_year = cube.extract(year_constraint)      
                    #print(" cube_recent_year = ", cube_recent_year)
                                                   
                    #try:
                    #    #print(" cube_recent_year.data = ", cube_recent_year.data)
                    #except:
                    #    print("no data")
                   
        
                    if(cube_recent_year):
                        print("in cube_recent_year")
        
                        # Average from time frequency to monthly mean 
                        try:
                            cube_monthly_recent_year = cube_recent_year.aggregated_by(['month'], iris.analysis.MEAN)
                            month_slice = cube_monthly_recent_year.extract(iris.Constraint(month=str(month_to_average)))

                            print("month_to_average=",month_to_average)

                            #print("SIZE / SHAPE")
                            #print(cube_monthly_recent_year.shape)
                            #print("")
                            #print("")                            
    
                            if(np.nonzero(month_slice)): 
                                #print("month_slice is non zero")
                                #print("month_slice",month_slice.data)
                                print("")

           
                            if(isinstance(month_slice, iris.cube.Cube)):
                                final_cube_list.append(month_slice)
                            else:
                                print("NOT A CUBE")
                        except:
                            print(cube_recent_year)
        
                        print("final_cube_list loop")
                        print("final_cube_list ",final_cube_list)
                
    
                        for cube in final_cube_list:

                            print("in final_cube_list cube.data=",cube.data)
    
                            for iobs in range(len(station_lon_array)):
    
                                print("file = ",file)
                                print("len(station_lon_array) = ",len(station_lon_array))
                                print("lat = ",station_lat_array[iobs]," lon = ",station_lon_array[iobs])

                                if(station_lat_array[iobs] < -8000):
                                    station_lat_array[iobs] = np.NaN
                                if(station_lon_array[iobs] < -8000):
                                    station_lon_array[iobs] = np.NaN
    
                                if (not math.isnan(station_lon_array[iobs])) and (not math.isnan(station_lat_array[iobs])):
                                    
                                    # Find lat / lon of the observation.  For N48
                                    index_lat = int((float(station_lat_array[iobs]) + 90.0) / float(2.5))
                                    index_lon = int((float(station_lon_array[iobs]) / float(3.75)))
                        
                                    print("in final_cube_list cube.data = ",cube.data)
                                    print("in final_cube_list cube.data = ",float(cube.data))
    
                                    if(np.isnan(cube_destination_empty.data[index_lat,index_lon])):    #If NaN then no previous obs data in this gridbox
                
                                        cube_destination_empty.data[index_lat,index_lon] = float(cube.data)
                                        cube_average_count.data[index_lat,index_lon] = cube_average_count.data[index_lat,index_lon] + 1.0

                                        print("A index_lat =",index_lat,"index_lon = ",index_lon)
                                        print("A cube_destination_empty.data[index_lat,index_lon] = ",cube_destination_empty.data[index_lat,index_lon])
                                        print("A cube_average_count.data[index_lat,index_lon] ",cube_average_count.data[index_lat,index_lon])
        
                                    else:
                                        ####cube_destination_empty.data[index_lat,index_lon] = float(cube.data)
                                        cube_destination_empty.data[index_lat,index_lon] = cube_destination_empty.data[index_lat,index_lon] + float(cube.data)
                                        cube_average_count.data[index_lat,index_lon] = cube_average_count.data[index_lat,index_lon] + 1.0

                                        print("B index_lat =",index_lat,"index_lon = ",index_lon)
                                        print("B cube_destination_empty.data[index_lat,index_lon] = ",cube_destination_empty.data[index_lat,index_lon])
                                        print("B cube_average_count.data[index_lat,index_lon] ",cube_average_count.data[index_lat,index_lon])

                                    
        
        # Average data in locations with more than one observation.
    
        # Mask zero values

        #print("before mask = ",cube_average_count.data)
        print("before mask mean= ",np.mean(cube_average_count.data))

        cube_average_count.data = ma.masked_where(cube_average_count.data == 0, cube_average_count.data)
        #cube_destination_empty = ma.masked_where(cube_average_count.data == 0, cube_destination_empty.data)
 
        #print("after mask mean= ",np.mean(cube_average_count.data))
        print("after mask = ",cube_average_count.data)


        #print("Bef bef bef2 cube_destination_empty.data =",cube_destination_empty.data[np.logical_not(np.isnan(cube_destination_empty.data))])

        #cube_destination_empty.data = ma.masked_invalid(cube_destination_empty.data)
        #cube_average_count.data = ma.masked_invalid(cube_average_count.data)

        #print("Bef cube_destination_empty.data =",cube_destination_empty.data[np.logical_not(np.isnan(cube_destination_empty.data))])

        #print("Bef cube_destination_empty.data",cube_destination_empty.data)
        #print("Bef cube_average_count.data",cube_average_count.data)

        #cube_destination_empty.data = ma.masked_invalid(cube_destination_empty.data)
        #cube_average_count.data = ma.masked_invalid(cube_average_count.data)

        #print("Aft cube_destination_empty.data",cube_destination_empty.data)
        #print("Aft cube_average_count.data",cube_average_count.data)

        print("bef division mean= ",np.nanmean(cube_destination_empty.data))

        #cube_destination_empty.data = cube_destination_empty.data / cube_average_count.data 
        print(cube_destination_empty)
        print(cube_average_count)

        #cube_destination_empty.data = iris.analysis.maths.divide(cube_destination_empty.data, cube_average_count.data)
        cube_destination_empty = iris.analysis.maths.divide(cube_destination_empty, cube_average_count)
        cube_destination_empty.long_name = str(variable_long_name)

        print("after division mean= ",np.mean(cube_destination_empty.data))
        #print("after division mean= ",np.mean(final.data))

        print("cube_average_count mean= ",np.mean(cube_average_count.data))
        print("cube_average_count = ",np.mean(cube_average_count.data))

        ##print("Aft cube_destination_empty.data =",cube_destination_empty.data[cube_destination_empty.data > 0])
        #print("Aft cube_destination_empty.data =",cube_destination_empty.data[np.logical_not(np.isnan(cube_destination_empty.data))])
 
        #print("dest empty nonzero = ",cube_destination_empty.data[cube_destination_empty.data > 0.0])

        cube_list = [cube_average_count, cube_destination_empty]
        
        if iSORPES:
            iris.save(cube_list,"/nfs/a201/earkpr/DataVisualisation/GASSP/"+str(variable_name)+"_Concentration_"+str(start_year)+"_"+str(final_year)+"_"+str(month_to_average)+"_LAMBDA_AVERAGED_SHIP_Savemoved_FixedUnits_SORPES.nc", netcdf_format='NETCDF3_CLASSIC')
        else:
            iris.save(cube_list,"/nfs/a201/earkpr/DataVisualisation/GASSP/"+str(variable_name)+"_Concentration_"+str(start_year)+"_"+str(final_year)+"_"+str(month_to_average)+"_LAMBDA_AVERAGED_SHIP_Savemoved_FixedUnits_ALLDATA_no_negative.nc", netcdf_format='NETCDF3_CLASSIC')
            
            
#%%            





sys.exit()




#%%

for coord in cube_monthly_recent_year.coords():
    print(coord.name())
    print(coord.standard_name)
    print(coord.points)
    print(coord.bounds)    
    print(coord.long_name)
    print(coord.units)
    print("")


#%%

np.nanmin(cubes[1].data)




sys.exit()


#%%


cubes = iris.load("/nfs/a201/earkpr/DataVisualisation/GASSP/Nigel_Code/Level2/VOCALS/COMP_ORG_AMS_VOCALS_Ship_R_RONALD_H._BROWN_2008-10-20_090000_2008-11-30.nc")


for cube in cubes:
    print(cube)
    
    






