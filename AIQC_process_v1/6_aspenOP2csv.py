"""
@author: Min Lun Wu
"""

import numpy as np
import pandas as pd
import datetime
import os
import math
import datetime as dt

from scipy.interpolate import interp1d

# %%
def interp_sounding(launchtime,data,res):    
    time=data['time']
    
    time_delta=(time-launchtime).apply(lambda x: x.seconds+x.microseconds/1000000)
    time_delta=time_delta

    P=data['P'].apply(lambda x: float(x))
    T=data['T'].apply(lambda x: float(x))
    RH=data['RH'].apply(lambda x: float(x))
    LAT=data['LAT'].apply(lambda x: float(x))
    LON=data['LON'].apply(lambda x: float(x))
    WD=data['WD'].apply(lambda x: float(x))
    WS=data['WS'].apply(lambda x: float(x))

    
# %%
    plev=np.append(max(P),np.arange(math.ceil(max(P))-1,math.floor(min(P))-1,res*-1))
    
    time_delta_itp=pd.Series(interp1d(P,time_delta,kind='nearest',fill_value='extrapolate')(plev))
    T_itp         =pd.Series(interp1d(P,T,fill_value='extrapolate')(plev))
    RH_itp        =pd.Series(interp1d(P,RH,fill_value='extrapolate')(plev))
    LAT_itp       =pd.Series(interp1d(P,LAT,fill_value='extrapolate')(plev))
    LON_itp       =pd.Series(interp1d(P,LON,fill_value='extrapolate')(plev))
    WD_itp        =pd.Series(interp1d(P,WD,fill_value='extrapolate')(plev))
    WS_itp        =pd.Series(interp1d(P,WS,fill_value='extrapolate')(plev))
    
# %%   
    IF_new=pd.Series(np.ones(len(plev)))
    time_itp=pd.Series(launchtime+pd.Series(time_delta_itp).apply(lambda x: dt.timedelta(seconds=float(x))))
    plev=pd.Series(plev)
    opdata=pd.concat([time_itp,plev,T_itp,RH_itp,LAT_itp,LON_itp,WD_itp,WS_itp,IF_new],axis=1)
    opdata.columns=['time','P','T','RH','LAT','LON','WD','WS','IF']
    
    return opdata

# %%
dpath='./L3_aspen/'
opath='./L4pr/'

files=[_ for _ in os.listdir(dpath) if _.endswith(".csv")]

#%% loop all files
for i in range(1): #range(len(files)):
    data=[]
    dfile=open(dpath+files[i],'r')
    # print(files[i])
    for line in dfile:
        data.append(line)
        
    launchtime=[x.strip() for x in data[1:7]]
    yyyy=int(launchtime[0].split(',')[1])
    mo=int(launchtime[1].split(',')[1])
    dd=int(launchtime[2].split(',')[1])
    hh=int(launchtime[3].split(',')[1])
    mi=int(launchtime[4].split(',')[1])
    ss=int(launchtime[5].split(',')[1])
    launchtime=dt.datetime(yyyy,mo,dd,hour=hh,minute=mi,second=ss)

    data=data[120::]
    clm=['field','time','P','T','RH','WS','WD','LAT','LON','Alt','GPS_Alt','Td','U','V','AScent']
    data=pd.DataFrame(list(i.split(',') for i in data),columns=clm)#.astype(float)
    data[data=='']=np.nan

    #%%
    time_delta=data.iloc[:,1].apply(lambda x: dt.timedelta(seconds=float(x)))
    # time_delta=data.iloc[:,1].apply(lambda x: float(x))
    time=time_delta+launchtime
    P=data.iloc[:,2]
    T=data.iloc[:,3]
    RH=data.iloc[:,4]
    WS=data.iloc[:,5]
    WD=data.iloc[:,6]
    lat=data.iloc[:,7]
    lon=data.iloc[:,8]   
    
    opdata=pd.concat([time,P,T,RH,lat,lon,WD,WS],axis=1)
    itp_data=interp_sounding(launchtime,opdata,1)

    # filename=files[i].replace('L3_aspen','L4pr')
    filename='L4pr.csv'
    opdata.to_csv(opath+filename,index=False)
    
    
