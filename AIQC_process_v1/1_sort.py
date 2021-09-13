"""
@author: Min Lun Wu
Stormtracker merged data sorting script prototype
"""

import numpy as np
import pandas as pd
import os
from datetime import datetime as dt

# from rh2q import *

#%%  file path & list setting
dpath='./L0/'
opath='./L1/'

files = [_ for _ in os.listdir(dpath) if _.endswith(".csv")]
log_file=open(opath+'L1_log.txt','w',newline='\n')

#%% loop all files
for i in range(len(files)):
    data=[]
    data=pd.DataFrame(pd.read_csv(dpath+files[i]))

    data.columns=data.columns.str.strip()
    data=data.sort_values(by='Time')

#%% find the first data
    vidx=pd.Series(np.ones(len(data)))
    P_tmp=data.iloc[:,5]
    for num in range(len(P_tmp)-11):
        down_P=0 ; first_P=0
        for af in range(0,10):
            if P_tmp[num+af] > P_tmp[num+af+1]:
               down_P=down_P+1
        if down_P==10:
           first_P=num
           break
    # print (first_P)
    
#%% if don't print error message on the screen
    if first_P==0:
        print(files[i]+" can't find first data")
        log_file.write(files[i]+" can't find first data"+'\n'+'\n')

        continue

#%% variable splitting
    time=data.iloc[:,0]
    launchtime=dt.strptime(time.iloc[first_P],'%Y/%m/%d %H:%M:%S.%f')
    # time=time.apply(lambda x: dt.strptime(x,'%Y/%m/%d %H:%M:%S.%f'))
    # time_delta=(time-launchtime).apply(lambda x: x.seconds)

    P=data.iloc[:,5]
    T=data.iloc[:,3]
    RH=data.iloc[:,4]
    LON=data.iloc[:,9]
    LAT=data.iloc[:,8]

    WS=data.iloc[:,14]/3.6
    WD=data.iloc[:,15]+180

    wd_corr= WD > 360
    WD[wd_corr]=WD[wd_corr]-360

    vidx[:first_P]=0        
    # valid_data=data
    # valid_data=data.iloc[first_P::,:]
    valid_data=pd.concat([time,P,T,RH,LON,LAT,WD,WS,vidx],axis=1)
    valid_data.columns=['time','P','T','RH','LAT','LON','WD','WS','IF']

#%% clear error value
    cleargrid=valid_data.query('P<=0|P>1050|T==-46.85|T==40.99|RH<=0').index.tolist()
    valid_data.loc[cleargrid,['P','RH','T']]=-9999
    valid_data.loc[cleargrid,'IF']=0
    
    vd_num=len(valid_data['IF'][valid_data['IF']==1])
    total_num=len(valid_data)
    ratio=vd_num/total_num*100
#%% output data
    #filename=files[i].strip('.csv')+'_L1.csv'
    filename='L1.csv'
    valid_data.to_csv(opath+filename,index=False)

#%% log file
    log_file.write(filename+'\n')
    log_file.write('-> launch time: '+launchtime.strftime('%Y-%m-%d %H:%M:%S')+'\n')
    log_file.write('-> valid data / total data: '+str(vd_num)+'/'+str(total_num)+' ('+str('%.3f' % ratio)+'%)'+'\n'+'\n')


log_file.close()



