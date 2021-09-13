"""
@author: Min Lun Wu
"""

import numpy as np
import pandas as pd
import datetime as dt
import os
import math

from scipy.interpolate import interp1d

# %%
def interp_sounding(data,res):
    IF=data.loc[:,'IF']
    
    time=data['time'].apply(lambda x: dt.datetime.strptime(x.replace('/','-'),'%Y-%m-%d %H:%M:%S.%f'))
    launchtime=time[min(IF[IF==1].index)]

    
    time_delta=(time-launchtime).apply(lambda x: x.seconds+x.microseconds/1000000)
    time_delta=time_delta[IF==1]

    P=data['P'][IF==1]
    T=data['T'][IF==1]
    T_new=data['T_new'][IF==1]
    RH=data['RH'][IF==1]
    RH_new=data['RH_new'][IF==1]
    LAT=data['LAT'][IF==1]
    LON=data['LON'][IF==1]
    WD=data['WD'][IF==1]
    WS=data['WS'][IF==1]
    U=data['U'][IF==1]
    V=data['V'][IF==1]
    q=data['q'][IF==1]
    q_new=data['q_new'][IF==1]
    rad=data['rad'][IF==1]
    
# %%
    plev=np.append(max(P),np.arange(math.ceil(max(P))-1,math.floor(min(P))-1,res*-1))
    
    time_delta_itp=pd.Series(interp1d(P,time_delta,kind='nearest',fill_value='extrapolate')(plev))
    T_itp         =pd.Series(interp1d(P,T,fill_value='extrapolate')(plev))
    T_new_itp     =pd.Series(interp1d(P,T_new,fill_value='extrapolate')(plev))
    RH_itp        =pd.Series(interp1d(P,RH,fill_value='extrapolate')(plev))
    RH_new_itp    =pd.Series(interp1d(P,RH_new,fill_value='extrapolate')(plev))
    LAT_itp       =pd.Series(interp1d(P,LAT,fill_value='extrapolate')(plev))
    LON_itp       =pd.Series(interp1d(P,LON,fill_value='extrapolate')(plev))
    WD_itp        =pd.Series(interp1d(P,WD,fill_value='extrapolate')(plev))
    WS_itp        =pd.Series(interp1d(P,WS,fill_value='extrapolate')(plev))
    U_itp         =pd.Series(interp1d(P,U,fill_value='extrapolate')(plev))
    V_itp         =pd.Series(interp1d(P,V,fill_value='extrapolate')(plev))
    q_itp         =pd.Series(interp1d(P,q,fill_value='extrapolate')(plev))
    q_new_itp     =pd.Series(interp1d(P,q_new,fill_value='extrapolate')(plev))
    rad_itp       =pd.Series(interp1d(P,rad,fill_value='extrapolate')(plev))
    
# %%   
    IF_new=pd.Series(np.ones(len(plev)))
    time_itp=pd.Series(launchtime+pd.Series(time_delta_itp).apply(lambda x: dt.timedelta(seconds=float(x))))
    plev=pd.Series(plev)
    opdata=pd.concat([time_itp,plev,T_itp,T_new_itp,RH_itp,RH_new_itp,LAT_itp,LON_itp,WD_itp,WS_itp,IF_new,U_itp,V_itp,q_itp,q_new_itp,rad_itp],axis=1)
    opdata.columns=['time','P','T','T_new','RH','RH_new','LAT','LON','WD','WS','IF','U','V','q','q_new','rad']
    
    return opdata

# %%
dpath='./L3/'
opath='./L4/'

files = [_ for _ in os.listdir(dpath) if _.endswith(".csv")]
res=1
for i in range(len(files)):
    data=[]
    data=pd.DataFrame(pd.read_csv(dpath+files[i]))
    
    itp_data=interp_sounding(data,res)
    
    #filename=files[i].replace('L3','L4')
    filename='L4.csv'
    itp_data.to_csv(opath+filename,index=False)
    
#%% log file
    log_file=open(opath+'L4_log.txt','w',newline='\n')
    log_file.write(filename+'\n')
    log_file.write('-> resolution: '+str(res)+' hPa\n')
    log_file.write('-> Max P: '+str('%.1f' %max(itp_data['P']))+' hPa\n')
    log_file.write('-> Min P: '+str(min(itp_data['P']))+' hPa\n')

    log_file.close()
