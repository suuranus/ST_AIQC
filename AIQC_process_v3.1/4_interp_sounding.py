"""
@author: Min Lun Wu
"""

import pandas as pd
import os
import sys

from interp_sounding import interp_sounding
from mkEOL import mkeol


# %%
dpath='./L3/'
opath='./L4/'

target=sys.argv[1]

res=1

if os.path.isfile(dpath+target):
    data=[]
    data=pd.DataFrame(pd.read_csv(dpath+target))
    
    opdata=interp_sounding(data,res)
    
    filename=target.replace('L3','L4')
    opdata.to_csv(opath+filename,index=False)
    
#%% log file
    log_file=open(opath+filename.replace('.csv','_log.txt'),'w',newline='\n')
    log_file.write(filename+'\n')
    log_file.write('-> resolution: '+str(res)+' hPa\n')
    log_file.write('-> Max P: '+str('%.1f' %max(opdata['P']))+' hPa\n')
    log_file.write('-> Min P: '+str(min(opdata['P']))+' hPa\n')

    log_file.close()
    
    # %%
    EOLdpath='./L4/'
    EOLopath='./L4/'

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


