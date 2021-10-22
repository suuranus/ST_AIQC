"""
@author: Min Lun Wu
AIQC_process_v2
"""

import numpy as np
import pandas as pd
import os
import datetime as dt
import sys

#%%  file path & list setting
#dpath='./L0/'
opath='./L1/'


data=[]
data=pd.DataFrame(pd.read_csv(sys.argv[1]))
strs=files.split('_')
ST_no=strs[1]

data.columns=data.columns.str.strip()
data=data.sort_values(by='Time').reset_index(drop=True)

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
if first_P==0 and num!=0:
    print(files+" can't find first data")
    no_first_data_log=open(opath+'no_first_data_list.txt','a',newline='\n')
    no_first_data_log.write(files+" can't find first data"+'\n')
    no_first_data_log.close()
    continue

#%% variable splitting
#ST_no=str(data['NodeID'][first_P])
channel=str(data['channel'][first_P])
time=data['Time']
time_bug_proof=dt.timedelta(microseconds=1)
time=time.apply(lambda x: dt.datetime.strptime(x,'%Y/%m/%d %H:%M:%S.%f')+time_bug_proof)

launchtime=time.iloc[first_P]
duration=(abs(time-launchtime)).apply(lambda x: x.seconds+x.microseconds/1000000)
duration[:first_P]=duration[:first_P]*-1
    
P=data['Pressure(hPa)']
T=data['Temperature(degree C)']
RH=data['Humidity(%)']
LON=data['Lon']
LAT=data['Lat']
GPS_Z=data['Height(m)']
WS=data['Speed(km/hr)']/3.6
WD=data['Direction(degree)']+180

wd_corr= WD > 360
WD[wd_corr]=WD[wd_corr]-360

vidx[:first_P]=0        
# valid_data=data
# valid_data=data.iloc[first_P::,:]
valid_data=pd.concat([duration,time,P,T,RH,WS,WD,LON,LAT,GPS_Z,vidx],axis=1).reset_index(drop=True)
valid_data.columns=['duration','time','P','T','RH','WS','WD','LON','LAT','GPS_Z','IF']
ori_num=len(valid_data)
    
#%% clear error value
cleargrid=valid_data.query('duration<0|P<=0|P>1050|T==-46.85|T==40.99|RH<=0').index.tolist()
opdata=valid_data.drop(cleargrid).reset_index(drop=True)
    
new_num=len(opdata)
ratio=new_num/ori_num*100
    
#%% output data
# filename=files[i].strip('.csv')+'_L1.csv'
# filename='L1.csv'
#filename='ST_'+launchtime.strftime('%Y%m%d%H')+'_no_'+ST_no+'_AIQCv2_L1.csv'
filename='no_'+ST_no+launchtime.strftime('_%Y%m%d_%H%M_')+'L1.csv'
opdata.to_csv(opath+filename,index=False)

#%% log file
log_file=open(opath+'L1_log.txt','w',newline='\n')
log_file.write(filename+'\n')
log_file.write('-> launch time: '+launchtime.strftime('%Y-%m-%d %H:%M:%S')+'\n')
log_file.write('-> valid data / total data: '+str(new_num)+'/'+str(ori_num)+' ('+str('%.3f' % ratio)+'%)'+'\n'+'\n')
log_file.close()
