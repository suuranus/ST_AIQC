"""
@author: Min Lun Wu
 input dataframe must contain duration( index name 'duration'), 
 time( index name 'time') and pressure( index name 'P')
"""

import numpy as np
import pandas as pd
import math
import datetime as dt

from scipy.interpolate import interp1d

# %%
def interp_sounding(data,res):
    
    index=data.columns
    duration=data['duration']
    time=data['time'].apply(lambda x: dt.datetime.strptime(x,'%Y-%m-%d %H:%M:%S.%f'))
    launchtime=time[duration==0]

    P=data['P']
    plev=np.append(max(P),np.arange(math.ceil(max(P))-1,math.floor(min(P))-1,res*-1))+1e-15
    P_new=pd.Series(plev)
    for i in range(len(index)):

        if index[i]=='duration' :
            tmp=data.iloc[:,i]
            tmp_itp=pd.Series(interp1d(P,tmp,kind='linear',fill_value='extrapolate')(plev))
            time_itp=tmp_itp.apply(lambda x: dt.timedelta(seconds=float(x))).apply(lambda x: x+launchtime)
            
            opdata=pd.concat([tmp_itp,time_itp,P_new],axis=1).reset_index(drop=True)

            del tmp, tmp_itp, time_itp
            continue
            
        if index[i]=='time' or index[i]=='P':
            continue
        
        tmp=data.iloc[:,i]
        tmp_itp=pd.Series(interp1d(P,tmp,kind='linear',fill_value='extrapolate')(plev))
        opdata=pd.concat([opdata,tmp_itp],axis=1).reset_index(drop=True)
        del tmp, tmp_itp

    opdata.columns=index
    return opdata