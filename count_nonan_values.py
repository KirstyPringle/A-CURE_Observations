
import iris
import numpy as np



months = ['FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']

for month in months:

    path1 = '/nfs/a173/earjsj/constraint/obsID_gblocation_infotables/KP_ObservationFiles/AODs_TOTAL/OLD_BugInValues_July2018/'
    file1 = 'AOD_440_2005_2015_'+str(month)+'_LAMBDA_AVERAGED.nc'

    path2 = '/nfs/a173/earjsj/constraint/obsID_gblocation_infotables/KP_ObservationFiles/AODs_TOTAL/'
    file2 = 'AOD_440_2005_2015_'+str(month)+'_26Aug_AVERAGED.nc'

    cube_withbug  = iris.load(path1+file1)
    cube_bugfixed = iris.load(path2+file2)

    print (month,'# observations = with bug ',np.count_nonzero(~np.isnan(cube_withbug[0].data)),' without bug', (np.count_nonzero(~np.isnan(cube_bugfixed[0].data))))

    index_withbug = np.argwhere(~np.isnan(cube_withbug[0].data))
    index_bugfixed = np.argwhere(~np.isnan(cube_bugfixed[0].data))

    # print('')
    # print('Are they identical?')
    # print(index_withbug == index_bugfixed)
    # print('')

    # print(index_bugfixed)

    print(' len = ',len(index_bugfixed))

    lat_bugfixed=[]
    lon_bugfixed=[]

    for i in index_bugfixed:

        lat_bugfixed.append(i[0])
        lon_bugfixed.append(i[1])

        # print('lat ',i[0], ' lon =',i[1])
        # print(i,cube_withbug[0].data[i[0],i[1]])

        if(np.isnan(cube_withbug[0].data[i[0],i[1]])):
            print('NAN!!!!!!!!!')


print('end')




