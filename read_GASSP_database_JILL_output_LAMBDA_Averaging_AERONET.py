
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

#variable_name = 'AOT_440'
variable_name = 'AOD_440'
variable_long_name = 'AOD_440_from_AERONET'

start_year = 2005
final_year = 2015
#start_year = 2010
#final_year = 2010

MonthDict = {   '01':'JAN',
                '02':'FRB',
                '03':'MAR',
                '04':'APR',
                '05':'MAY',
                '06':'JUN',
                '07':'JUL',
                '08':'AUG',
                '09':'SEP',
                '10':'OCT',
                '11':'NOV',
                '12':'DEC'  }



# Location of GASSP data
path = '/nfs/a201/earkpr/DataVisualisation/GASSP/AERONET/AOT/LEV20/monave/'
# path = '/nfs/a201/earkpr/DataVisualisation/GASSP/AERONET/AOT/LEV20/monave/JULY/'
# path = '/nfs/a201/earkpr/DataVisualisation/GASSP/AERONET/AOT/LEV20/monave/OLD/JULY/'

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
print(cube_destination_empty.data)

cube_average_count = cube_dest.copy()
cube_average_count.data[:,:] = 0.0
print(cube_average_count.data)
cube_average_count.long_name = "Array to count number of stations contributing to the data"
cube_average_count.var_name = "observations_counter"


#iris.save(cube_destination_empty, "/nfs/a201/earkpr/DataVisualisation/GASSP/Destination_netCDF.nc")


#%%



for imonth, month in MonthDict.iteritems():
    print("key = ",imonth," value = ",month)

    ncfiles = []
    for root, dirs, files in os.walk(str(path)):
        for file in files: 
            if file.endswith(str(imonth)+'_v3_mav_rec.nc'):
                print("file = ",file)

                file_year = file[-21:-17]
                print ("file_year = ",int(file_year))

                # Select files within the year of interest (inclusive)
                if(start_year <= int(file_year) <= final_year):
                    print ("CHOSEN file_year = ",file_year)

                if str(variable_name) in file:           
                    if str("T") in file:           
                        ncfiles.append(os.path.join(root, file))
 
    for file in ncfiles:

        cubes = iris.load(file)
        print(cubes)
   
        for cube in cubes:

            if(cube.var_name == str(variable_name)):
                print("cube.var_name",cube.var_name)
                aod_data = cube.data
                print("aod_data = ",aod_data)

            if(cube.var_name == 'latitude'):
                station_lat = cube.data[0]

            if(cube.var_name == 'longitude'):
                station_lon = cube.data[0]

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

    iris.save(cube_list,"/nfs/a201/earkpr/DataVisualisation/GASSP/"+str(variable_name)+"_"+str(start_year)+"_"+str(final_year)+"_"+str(month)+"_LAMBDA_AVERAGED.nc")


sys.exit()





