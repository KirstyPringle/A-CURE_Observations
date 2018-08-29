
# K. Pringle
#
# Code to convert GASSP Level 2 data onto a destination gridded netCDF grid.
# Code will also create average of a single month (e.g. July) over multiple years.


import iris
import numpy as np
import sys
import datetime
from iris.time import PartialDateTime
import matplotlib.pyplot as plt

iris.FUTURE.netcdf_no_unlimited=True

import iris.coord_categorisation
import datetime
import iris.unit
import cf_units
import numpy.ma as ma
import os
import re

from six.moves import (filter, input, map, range, zip)  # noqa
import iris.quickplot as qplt
from matplotlib.colors import from_levels_and_colors


#%%

# User settings
#variable_name = 'PM2P5'
#variable_long_name = 'PM2P5 Concentrations from PPE on Masaru grid'

#variable_name = 'ORG'
#variable_long_name = 'ORG_Concentrations_from_GASSP'

#variable_name = 'AOT_440'
variable_name = 'AOD_440'
variable_long_name = 'AOD_440_from_AERONET'

#start_year = 2005
#final_year = 2015
start_year = 2005
final_year = 2015
##final_year = 2005

MonthDict = {   '01':'JAN',
                '02':'FEB',
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

#MonthDict = {   '01':'JAN',
#                '02':'FEB',
#                '03':'MAR' }

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
#%%

for imonth, month in MonthDict.iteritems():

    cube_destination_empty = cube_dest.copy()
    cube_destination_empty.data[:,:] = np.nan
    cube_destination_empty.long_name = str(variable_long_name)
    cube_destination_empty.var_name = str(variable_name) 

    cube_average_count = cube_dest.copy()
    cube_average_count.data[:,:] = np.nan
    cube_average_count.long_name = "Array to count number of stations contributing to the data"
    cube_average_count.var_name = "observations_counter"

    aod_average_alldata = float(0.0)
    aod_total_alldata = float(0.0)

    print("key = ",imonth," value = ",month)
    ncfiles = []

    for root, dirs, files in os.walk(str(path)):
        for file in files: 
            if file.endswith(str(imonth)+'_v3_mav_rec.nc'):

                file_year = file[-21:-17]

                # Select files within the year of interest (inclusive)
                if(start_year <= int(file_year) <= final_year):
                   ## print ("CHOSEN file_year = ",file_year)
#
                    if str(variable_name) in file:           
                       ##if str("Toronto") in file:           
                        ncfiles.append(os.path.join(root, file))

    ##print(ncfiles)

    station_lon_array = []
    station_lat_array = []
    aod_data_array = []

    for file in ncfiles:

        cubes = iris.load(file)
        #print(cubes)
   
        for cube in cubes:

            if(cube.var_name == str(variable_name)):
                #print("cube.var_name",cube.var_name)
                aod_data = cube.data
                aod_total_alldata = aod_total_alldata + aod_data
                aod_average_alldata = aod_average_alldata + aod_data
                aod_data_array.append(aod_data)

            if(cube.var_name == 'latitude'):
                station_lat = cube.data[0]

            if(cube.var_name == 'longitude'):
                station_lon = cube.data[0]

        station_lon_array.append(station_lon)
        station_lat_array.append(station_lat)


        # Find lat / lon of the observation.  For N48

        # Find the gridbox the observation falls in.
        index_lat = int((float(station_lat) + 90.0) / float(2.5))
        index_lon = int((float(station_lon) / float(3.75)))

        # Find the distance between station_lat and all gridbox centers.

        # convert from -180 : 180 to 0 : 360 
        if station_lon < 0:
            station_lon = 360 + station_lon 

        lat_distance = np.absolute(station_lat - cube_destination_empty.coord('latitude').points)
        lon_distance = np.absolute(station_lon - cube_destination_empty.coord('longitude').points)

        lat_index_min_distance =  np.where(lat_distance == lat_distance.min())
        lon_index_min_distance =  np.where(lon_distance == lon_distance.min())

        index_lat = lat_index_min_distance
        index_lon = lon_index_min_distance

        #if(aod_data > 0.0):
        #    print("cube.data > 0.0 = ",aod_data)
        #    print("cube.data > 0.0 = ",np.float(aod_data))

        if(np.isnan(cube_destination_empty.data[index_lat,index_lon])):    #If NaN then no previous obs data in this gridbox
            cube_destination_empty.data[index_lat,index_lon] = float(aod_data)
            cube_average_count.data[index_lat,index_lon] = float(1.0)
        else:
            cube_destination_empty.data[index_lat,index_lon] = cube_destination_empty.data[index_lat,index_lon] + float(aod_data)
            cube_average_count.data[index_lat,index_lon] = cube_average_count.data[index_lat,index_lon] + float(1.0)


    # Average data in locations with more than one observation.
    cube_destination_empty.data = cube_destination_empty.data / cube_average_count.data

    print("PRINTING")
    print("cube_average_count = ",cube_average_count.data)
    print("")
    print("COUNT MAX = ",np.nanmax(cube_average_count.data))
    print("COUNT MEAN = ",np.nanmean(cube_average_count.data))
    print("COUNT MIN = ",np.nanmin(cube_average_count.data))
    print("")
    print("MAX = ",np.nanmax(cube_destination_empty.data))
    print("MEAN = ",np.nanmean(cube_destination_empty.data))
    print("MEAN AOD_DATA_ARRAY = "), np.nanmean(aod_data_array)
    print("MIN = ",np.nanmin(cube_destination_empty.data))
    print("")
    print("")
    print("")

    #print(cube_destination_empty.data)

    cube_list = [cube_destination_empty, cube_average_count]

    iris.save(cube_list,"/nfs/a201/earkpr/DataVisualisation/GASSP/Files_For_Jill/"+str(variable_name)+"_"+str(start_year)+"_"+str(final_year)+"_"+str(month)+"_26Aug_AVERAGED.nc")

    if month == 0:
        nice_cmap = plt.get_cmap('brewer_PuBuGn_09')
        colors = nice_cmap([4, 5, 6, 7, 8, 9 ])
        levels = [0.0001, 0.001,  0.01, 0.1, 1.0, 10, 100 ]
        cmap, norm = from_levels_and_colors(levels, colors)

        plt.subplot(1, 2, 1)

        # Draw the block plot.
        qplt.pcolormesh(cube_destination_empty, cmap=cmap, norm=norm)

        plt.gca().coastlines()
        plt.plot(station_lon_array, station_lat_array, linestyle='none', marker="o", markersize=0.5, alpha=0.6, c="orange", markeredgewidth=1)
        #plt.plot(station_lon_array, station_lat_array, linestyle='none', marker="o", markersize=0.5, alpha=0.6, c=, markeredgewidth=1)

        #    qplt.drawparallels(np.arange(int(40.125),int(44.625),1),labels=[1,0,0,0])
        #    qplt.drawmeridians(np.arange(int(-71.875),int(-66.375),1),labels=[0,0,0,1])

        plt.savefig("/nfs/a201/earkpr/DataVisualisation/GASSP/Files_For_Jill/AERONET_Sites_and_Gridboxes.ps")




