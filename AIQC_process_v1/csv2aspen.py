"""
@author: Min Lun Wu
"""
import numpy as np
import pandas as pd
import os
import datetime as dt

def csv2asp(IF,time,P,T,RH,LAT,LON,WD,WS,logfile_full_path,opfile):
# %%
    time=time.apply(lambda x: dt.datetime.strptime(x.replace('/','-'),'%Y-%m-%d %H:%M:%S.%f'))
    launchtime=time[min(IF[IF==1].index)]
    time_delta=(time-launchtime).apply(lambda x: x.seconds)
    time_delta=time_delta[IF==1]
    
    opdata=pd.concat([time_delta,P,T,RH,LAT,LON,WD,WS],axis=1)
    opdata.columns=['time','P','T','RH','LAT','LON','WD','WS']
    opdata.insert(0,'field','Data',True)

# %%
    log=[]
    if os.path.isfile(logfile_full_path):
       log_file=open(logfile_full_path,'r')
       for line in log_file:
           log.append(line)
           log=str(log).strip("[']").split(',')
           log=['Nan' if x=='-9999' else x for x in log]
       log_file.close()
    else:
        log=['Nan']*18
# %%
    opfile.write('FileFormat,CSV\n')
    
    if log[3]=='Nan':
        opfile.write('Year,'+launchtime.strftime('%Y')+'\n')
        opfile.write('Month,'+launchtime.strftime('%m')+'\n')
        opfile.write('Day,'+launchtime.strftime('%d')+'\n')
        opfile.write('Hour,'+launchtime.strftime('%H')+'\n')
        opfile.write('Minute,'+launchtime.strftime('%M')+'\n')
        opfile.write('Second,'+launchtime.strftime('%S')+'\n')
    else:
        opfile.write('Year,'+log[0]+'\n')
        opfile.write('Month,'+log[1]+'\n')
        opfile.write('Day,'+log[2]+'\n')
        opfile.write('Hour,'+log[3]+'\n')
        opfile.write('Minute,'+log[4]+'\n')
        opfile.write('Second,'+log[5]+'\n')
        
    if os.path.isfile(logfile_full_path):
        opfile.write('ST ID,'+log[6]+'\n')
        opfile.write('Launch Site,'+log[7]+'\n')
        opfile.write('Launch Latitude,'+log[8]+'\n')
        opfile.write('Launch Longitude,'+log[9]+'\n')
        opfile.write('Launch Altitude,'+log[10]+'\n')
        opfile.write('Station P (hPa),'+log[11]+'\n')
        opfile.write('Station T (deg C),'+log[12]+'\n')
        opfile.write('Station RH (%),'+log[13]+'\n')
        opfile.write('Station WD (deg),'+log[14]+'\n')
        opfile.write('Station WS (m/s),'+log[15]+'\n')
        opfile.write('Cloud fraction (1~10),'+log[16]+'\n')
        opfile.write('rain (0/1),'+log[17]+'\n')
    else:
        opfile.write('ST ID,'+'Nan'+'\n')
        opfile.write('Launch Site,'+'Nan'+'\n')
        opfile.write('Launch Latitude,'+'Nan'+'\n')
        opfile.write('Launch Longitude,'+'Nan'+'\n')
        opfile.write('Launch Altitude,'+'Nan'+'\n')
        opfile.write('Station P (hPa),'+'Nan'+'\n')
        opfile.write('Station T (deg C),'+'Nan'+'\n')
        opfile.write('Station RH (%),'+'Nan'+'\n')
        opfile.write('Station WD (deg),'+'Nan'+'\n')
        opfile.write('Station WS (m/s),'+'Nan'+'\n')
        opfile.write('Cloud fraction (1~10),'+'Nan'+'\n')
        opfile.write('rain (0/1),'+'Nan'+'\n')
    
    opfile.write('Fields,time,Pressure,Temperature,RH,Latitude,Longitude,Direction,Speed\n')
    opfile.write('Units,sec,mb,deg C,%,deg,deg,deg,m/s\n')
    opdata.to_csv(opfile,index=False,header=False)
    opfile.close()

    return opfile

