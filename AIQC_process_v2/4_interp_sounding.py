"""
@author: Min Lun Wu
"""

import pandas as pd
import os

from interp_sounding import interp_sounding
from mkEOL import mkeol


# %%
dpath='./L3/'
opath='./L4/'

files = [_ for _ in os.listdir(dpath) if _.endswith(".csv")]

res=1

for i in range(len(files)):
    data=[]
    data=pd.DataFrame(pd.read_csv(dpath+files[i]))
    
    opdata=interp_sounding(data,res)
    
    #filename=files[i].replace('L3','L4')
    filename='L4.csv'
    opdata.to_csv(opath+filename,index=False)
    
#%% log file
    log_file=open(opath+'L4_log.txt','w',newline='\n')
    log_file.write(filename+'\n')
    log_file.write('-> resolution: '+str(res)+' hPa\n')
    log_file.write('-> Max P: '+str('%.1f' %max(opdata['P']))+' hPa\n')
    log_file.write('-> Min P: '+str(min(opdata['P']))+' hPa\n')

    log_file.close()
    
# %%
dpath='./L4/'
opath='./L4/'

files = [_ for _ in os.listdir(dpath) if _.endswith(".csv")]

for i in range(len(files)):
    data=[]
    data=pd.DataFrame(pd.read_csv(dpath+files[i]))
    launch_info=data.iloc[1,:]
    eol_data=data.loc[:,['duration','time','P','T','Td','RH','U','V','WS','WD','dZ','geoALT','LON','LAT','GPS_Z']].reset_index(drop=True)
    eol_data.columns=['duration','time','P','T','Td','RH','U','V','WS','WD','dZ','geoALT','LON','LAT','GPS_Z']
    
    filename='L4.eol'
    
    opfile = open(opath+filename, "w",newline='\n')
    mkeol(eol_data,opfile,'4',lon=launch_info['LON'],lat=launch_info['LAT'],alt=launch_info['GPS_Z'])
    opfile.close()
