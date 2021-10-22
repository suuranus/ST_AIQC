"""
@author: Min Lun Wu
AIQC_process_v2
"""

import numpy as np
import pandas as pd
import os
import sys

from datetime import datetime
from rh2q import rh_to_q
from rh2td import rh2td

from geo_height import geo_height
from solar_radiation import solar
from mkEOL import mkeol

# %%
dpath='./L1/'
opath='./L2/'

target=sys.argv[1]

if os.path.isfile(dpath+target):
    data=[]
    data=pd.DataFrame(pd.read_csv(dpath+target))

#%%
    duration=data['duration']
    time=data['time']
    time=time.apply(lambda x: datetime.strptime(x,'%Y-%m-%d %H:%M:%S.%f'))
    
    P=data['P']
    T=data['T']
    RH=data['RH']
    WS=data['WS']
    WD=data['WD']
    LON=data['LON']
    LAT=data['LAT']
    GPS_Z=data['GPS_Z']
    IF=data['IF']

#%% 
    launchtime=time[duration==0]
    llh=GPS_Z[duration==0]
    llp=P[duration==0]
    
    if len(launchtime) > 1:
       launchtime=launchtime[len(launchtime)-1]
       llh=llh[len(llh)-1]
       llp=llp[len(llp)-1]
    
    U=-1*WS*np.sin(WD*np.pi/180)
    V=-1*WS*np.cos(WD*np.pi/180)
   
    geo_Z=pd.Series(geo_height(llh,P,T,llp))

    dZ=geo_Z.diff()
    dZ[0]=0.0
    
    Q,QS=rh_to_q(P,T,RH)
    
    Td=pd.Series(rh2td(T,RH))

    yyyy=time.apply(lambda x: x.strftime('%Y'))
    mm=time.apply(lambda x: x.strftime('%m'))
    dd=time.apply(lambda x: x.strftime('%d'))
    lt=time.apply(lambda x: int(x.strftime('%H')))

    rad=pd.Series(solar(yyyy,mm,dd,lt,LAT,LON))

#%%  
    opdata=pd.concat([duration,time,P,T,Td,RH,U,V,WS,WD,dZ,geo_Z,LON,LAT,GPS_Z,Q,rad],axis=1).reset_index(drop=True)
    opdata.columns=['duration','time','P','T','Td','RH','U','V','WS','WD','dZ','geoALT','LON','LAT','GPS_Z','q','rad']

# %%
    # filename=files[i].replace('L1','L2')
    #filename='L2.csv'
    opfilename=target.replace('L1','L2')

    opdata.to_csv(opath+opfilename,index=False)

    
# %%
    EOLdpath='./L2/'
    EOLopath='./L2/'

    if os.path.isfile(EOLdpath+opfilename):
        data=[]
        data=pd.DataFrame(pd.read_csv(EOLdpath+opfilename))

        launch_info=data.iloc[1,:]

        eol_data=data.loc[:,['duration','time','P','T','Td','RH','U','V','WS','WD','dZ','geoALT','LON','LAT','GPS_Z']].reset_index(drop=True)
        eol_data.columns=['duration','time','P','T','Td','RH','U','V','WS','WD','dZ','geoALT','LON','LAT','GPS_Z']

        EOL_filename=opfilename.replace('.csv','.eol')
        EOLopfile = open(EOLopath+EOL_filename, "w",newline='\n')
        mkeol(eol_data,EOLopfile,'2',lon=launch_info['LON'],lat=launch_info['LAT'],alt=launch_info['GPS_Z'])
        EOLopfile.close()

else:
    print("No corresponding file "+target+" exist")
