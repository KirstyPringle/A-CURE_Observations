
# K. Pringle
#
# Code to convert GASSP Level 2 data onto a destination gridded netCDF grid.
# Code will also create average of a single month (e.g. July) over multiple years.


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


#%%

# User settings
#variable_name = 'PM2P5'
#variable_long_name = 'PM2P5 Concentrations from PPE on Masaru grid'

#variable_name = 'ORG'
#variable_long_name = 'ORG_Concentrations_from_GASSP'

variable_name = 'AOT_440'
variable_long_name = 'AOT_440_from_AERONET'

start_year = 2005
final_year = 2010
month_to_average = 'Jul'  #  Need to use IRIS month naming convention.  Three letter month name


# Location of GASSP data
path = '/nfs/a201/earkpr/DataVisualisation/GASSP/AERONET/AOT/LEV20/monave/JULY/'

# path = '/nfs/a201/earkpr/DataVisualisation/GASSP/Nigel_Code/Level2/'

#%%

#  Read in file on destination grid

file_destination = "/nfs/a201/earkpr/DataVisualisation/GASSP/N48_Lon_Lat_Grid.nc"
cube_destination = iris.load(file_destination)


#print(cube_destination)
#for coord in cube_destination[0].coords():
#    ##print("coord = ",coord)
#    print("coord.long_name = ",coord.long_name)
#    print("coord.name = ",coord.name)
#    print("coord.points = ",coord.points)
#    print("coord.units = ",coord.units)
#    print("coord.var_name = ",coord.var_name)


#  Just take a lat / lon grid (ignore realization, time and hybrid_ht)

test_temp = cube_destination[0]
test = test_temp[0, 0, 0, :, :]

cube_dest = test

cube_destination_empty = cube_dest.copy()
cube_destination_empty.data[:,:] = np.nan
cube_destination_empty.long_name = str(variable_long_name)
cube_destination_empty.var_name = str(variable_name) 
print(cube_destination_empty.data)

cube_average_count = cube_dest.copy()
cube_average_count.data[:,:] = 0.0
print(cube_average_count.data)
cube_average_count.long_name = "Array to count number of stations contributing to the data"
cube_average_count.var_name = "observations_counter"


#iris.save(cube_destination_empty, "/nfs/a201/earkpr/DataVisualisation/GASSP/Destination_netCDF.nc")


#%%

ncfiles = []
for root, dirs, files in os.walk(str(path)):
#for root, dirs, files in os.walk('/nfs/a201/earkpr/DataVisualisation/GASSP/'):
  for file in files: 
    if file.endswith('.nc'):
        ##file_year = file[-10:-6]
        file_year = file[-18:-14]

        print ("file_year = ",float(file_year))

        # Select files within the year of interest (inclusive)
        if(start_year <= float(file_year) <= final_year):
            print ("CHOSEN file_year = ",file_year)

            if str(variable_name) in file:           
##                if str("Toronto") in file:           
                ncfiles.append(os.path.join(root, file))
 
print("ncfiles")
print(ncfiles)

# Read all cubes in list 
#cube_list = iris.load(ncfiles)


for file in ncfiles:

    cubes = iris.load(file)
   
    for cube in cubes:

        if(cube.var_name == str(variable_name)):
            print("cube.var_name",cube.var_name)
            aod_data = cube.data
            print("aod_data = ",aod_data)

        if(cube.var_name == 'latitude'):
            station_lat = cube.data

        if(cube.var_name == 'longitude'):
            station_lon = cube.data

    print("station_lon = ",station_lon)
    print("station_lat = ",station_lat)


    # Find lat / lon of the observation.  For N48

    index_lat = int((float(station_lat) + 90.0) / float(2.5))
    index_lon = int((float(station_lon) / float(3.75)))

    print(" index_lat = ", index_lat,"station_lat = ",station_lat)
    print(" index_lon = ",index_lon, "station_lon = ",station_lon)
    
    if(aod_data > 0.0):
        print("cube.data > 0.0 = ",aod_data)
        print("cube.data > 0.0 = ",np.float(aod_data))

    if(np.isnan(cube_destination_empty.data[index_lat,index_lon])):    #If NaN then no previous obs data in this gridbox
        cube_destination_empty.data[index_lat,index_lon] = float(aod_data)
        cube_average_count.data[index_lat,index_lon] = cube_average_count.data[index_lat,index_lon] + 1.0
    else:
        cube_destination_empty.data[index_lat,index_lon] = cube_destination_empty.data[index_lat,index_lon] + float(aod_data)
        cube_average_count.data[index_lat,index_lon] = cube_average_count.data[index_lat,index_lon] + 1.0


# Average data in locations with more than one observation.

print("PRINTING")
print(cube_destination_empty.data)
print(cube_average_count.data)

cube_destination_empty.data = cube_destination_empty.data / cube_average_count.data

print(cube_destination_empty.data)

cube_list = [cube_destination_empty, cube_average_count]

#%%

iris.save(cube_list,"/nfs/a201/earkpr/DataVisualisation/GASSP/"+str(variable_name)+"_Concentration_"+str(start_year)+"_"+str(final_year)+"_LAMBDA_AVERAGED.nc")


sys.exit()



















    #print(cube.attributes['Longitude'])


#  Remove degE and degN from the naming
#for cube in cube_list:
# 
#    #  Remove the N and E and degN and degE characters from lat / lon string
#    print("BEF =",cube.attributes['Station_Lon'])
#    cube.attributes['Station_Lon'] = only_numerics(cube.attributes['Station_Lon'])
#    cube.attributes['Station_Lat'] = only_numerics(cube.attributes['Station_Lat'])
#    print("AFT1 =",cube.attributes['Station_Lon'])
#    
#    # Convert lon from -180 to 180 to 0 to 360    
#    if(float(cube.attributes['Station_Lon']) < 0 ):
#        cube.attributes['Station_Lon'] = 360.0 + float(cube.attributes['Station_Lon']) 
#        
#    print("AFT2 =",cube.attributes['Station_Lon'])
#    print()
#    #print("Final Lon = ",float(cube.attributes['Station_Lon']))
#    #print("Final Lat = ",float(cube.attributes['Station_Lat']))
#   
#    # Convert any data from ng m-3 to ug m-3
#    print(cube.units)
#    if(cube.units == "ng m-3"):
#        cube.convert_units('ug m-3')
#        print(cube.units)
#        print("")
#
#%%

# Define new time axis
new_time_unit = iris.unit.Unit('seconds since 1970-01-01 00:00:00', calendar='gregorian')

final_cube_list=[]

#for cube in cube_list:
#    for coord in cube.coords():
#        ##print("coord = ",coord)
#        print("coord.long_name = ",coord.long_name)
#        print("coord.name = ",coord.name)
#        print("coord.units = ",coord.units)
#        print("coord.var_name = ",coord.var_name)
#
#sys.exit()

#%%
#for  cube in enumerate(cube_list):
    
for  cube in cube_list:
    if(cube.var_name == str(variable_name)):

        for coord in cube.coords():
            #print("coord.name() = ",coord.name())
            #print("coord.long_name = ",coord.long_name)

            # No longer needed as fixed GASSP data time label.
            if(coord.long_name == 'Time in seconds'):
                coord.convert_units(new_time_unit)

            if(coord.long_name == 'Time in seconds'):
                iris.coord_categorisation.add_year(cube, 'Time in seconds',  name='year')
                iris.coord_categorisation.add_month(cube, 'Time in seconds',  name='month')
                iris.coord_categorisation.add_month_number(cube, 'Time in seconds' , name='month_number')

        # Select data that is between start_year to  final_year  (cube_recent_year)
        year_constraint = iris.Constraint(year=lambda cell: start_year < cell < final_year)
        cube_recent_year = cube.extract(year_constraint)

        if(cube_recent_year):

            # Average from time frequency to monthly mean 
            cube_monthly_recent_year = cube_recent_year.aggregated_by(['month'], iris.analysis.MEAN)
                
            # Just select month_to_average data, e.g. just July data
            month_slice = cube_monthly_recent_year.extract(iris.Constraint(month=str(month_to_average)))
                    
            if(isinstance(month_slice, iris.cube.Cube)):
                final_cube_list.append(month_slice)
            else:
                print("NOT A CUBE")
                    

#%%

print("final_cube_list loop")
print(final_cube_list)

#%%

for cube in final_cube_list:

    if(cube.var_name == str(variable_name)):
        for coord in cube.coords():
            if(coord.var_name == "longitude"):
                print (cube.var_name)
                print("coord.points = ",coord.points)
                station_lat = coord.points
            if(coord.var_name == "latitude"):
                print (cube.var_name)
                print("coord.points = ",coord.points)
                station_lon = coord.points

    # Find lat / lon of the observation.  For N96
    #index_lat = int((float(station_lat) + 90.0) / float(1.25))
    #index_lon = int((float(station_lon) / float(1.875)))

    # Find lat / lon of the observation.  For N48
    index_lat = int((float(station_lat) + 90.0) / float(2.5))
    index_lon = int((float(station_lon) / float(3.75)))
    
    if (cube.var_name == str(variable_name)):
        print("CUBE.DATA = ",float(cube.data))

        if(np.isnan(cube_destination_empty.data[index_lat,index_lon])):    #If NaN then no previous obs data in this gridbox

          cube_destination_empty.data[index_lat,index_lon] = float(cube.data)
          cube_average_count.data[index_lat,index_lon] = cube_average_count.data[index_lat,index_lon] + 1.0

        else:

          cube_destination_empty.data[index_lat,index_lon] = cube_destination_empty.data[index_lat,index_lon] + float(cube.data)
          cube_average_count.data[index_lat,index_lon] = cube_average_count.data[index_lat,index_lon] + 1.0

# Average data in locations with more than one observation.
cube_destination_empty.data = cube_destination_empty.data / cube_average_count.data 

cube_list = [cube_destination_empty, cube_average_count]

#%% 

iris.save(cube_list,"/nfs/a201/earkpr/DataVisualisation/GASSP/"+str(variable_name)+"_Concentration_"+str(start_year)+"_"+str(final_year)+"_"+str(month_to_average)+"_LAMBDA_AVERAGED.nc")
    

sys.exit()

