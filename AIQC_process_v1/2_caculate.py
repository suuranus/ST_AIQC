import numpy as np
import pandas as pd
import os

from datetime import datetime
from rh2q import rh_to_q
from solar_radiation import solar

# %%
dpath='./L1/'
opath='./L2/'

files = [_ for _ in os.listdir(dpath) if _.endswith(".csv")]

for i in range(len(files)):
    data=[]
    data=pd.DataFrame(pd.read_csv(dpath+files[i]))

#%%
    time=data.loc[:,'time']
    time=time.apply(lambda x: datetime.strptime(x,'%Y/%m/%d %H:%M:%S.%f'))
    
    P=data['P']
    T=data['T']
    RH=data['RH']
    LON=data['LON']
    LAT=data['LAT']
    WS=data['WS']
    WD=data['WD']
    IF=data['IF']
    
    U=-1*WS*np.sin(WD*np.pi/180)
    V=-1*WS*np.cos(WD*np.pi/180)
    
    Q,QS=rh_to_q(P,T,RH)
    # Q[IF==0]=-9999

    yyyy=time.apply(lambda x: x.strftime('%Y'))
    mm=time.apply(lambda x: x.strftime('%m'))
    dd=time.apply(lambda x: x.strftime('%d'))
    lt=time.apply(lambda x: int(x.strftime('%H')))

    rad=solar(yyyy,mm,dd,lt,LAT,LON)
    data=pd.concat([data,U,V,Q,pd.Series(rad)],axis=1)
    data.columns=['time','P','T','RH','LAT','LON','WD','WS','IF','U','V','q','rad']

# %%
    #filename=files[i].replace('L1','L2')
    filename='L2.csv'
    data.to_csv(opath+filename,index=False)   
