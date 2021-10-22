"""
@author: Min Lun Wu
"""

import pandas as pd
import os
import sys
import datetime as dt

from interp_sounding import interp_sounding
from mkEOL import mkeol


# %%
dpath='./L3_aspen/'
opath='./L4_aspen/'

target=sys.argv[1]

#%% loop all files
if os.path.isfile(dpath+target):
    data=[]
    dfile=open(dpath+target,'r')
    # print(files[i])
    for line in dfile:
        data.append(line)

    launchtime=dt.datetime.strptime(data[5][-23:],'%Y, %m, %d, %H:%M:%S ')
    data=data[14::]
    
    #%%
    clm=['duration','hh','mm','ss','P','T','Td','RH','U','V','WS','WD','dZ','geoALT','LON','LAT','GPS_Z']
    data=pd.DataFrame(list(i.split() for i in data),columns=clm).drop(['hh','mm','ss'], axis=1).astype(float)

    #%%
    data['duration'][0]=0
    duration=data['duration'].apply(lambda x: dt.timedelta(seconds=float(x)))

    time=(duration+launchtime).apply(lambda x : x.strftime('%Y-%m-%d %H:%M:%S.%f'))
    data.insert(1,'time',time,True)
    
    res=1
    opdata=interp_sounding(data,res)
    
    filename=target.replace('_L3_aspen.eol','_L4_aspen.csv')
    opdata.to_csv(opath+filename,index=False)


    # %%
    EOLdpath='./L4_aspen/'
    EOLopath='./L4_aspen/'

    if os.path.isfile(EOLdpath+filename):
        data=[]
        data=pd.DataFrame(pd.read_csv(EOLdpath+filename))

        launch_info=data.iloc[1,:]

        eol_data=data.loc[:,['duration','time','P','T','Td','RH','U','V','WS','WD','dZ','geoALT','LON','LAT','GPS_Z']].reset_index(drop=True)
        eol_data.columns=['duration','time','P','T','Td','RH','U','V','WS','WD','dZ','geoALT','LON','LAT','GPS_Z']

        EOL_filename=filename.replace('.csv','.eol')
        EOLopfile = open(EOLopath+EOL_filename, "w",newline='\n')
        mkeol(eol_data,EOLopfile,'2',lon=launch_info['LON'],lat=launch_info['LAT'],alt=launch_info['GPS_Z'])
        EOLopfile.close()

else:
    print("No corresponding file "+target+" exist")

