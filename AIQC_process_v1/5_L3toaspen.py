"""
@author: Min Lun Wu
"""

import numpy as np
import pandas as pd
import datetime as dt
import os

from csv2aspen import csv2asp

# %%
dpath='./L3/'
opath='./L3pr/'

files = [_ for _ in os.listdir(dpath) if _.endswith(".csv")]
res=1
for i in range(len(files)):
    data=[]
    data=pd.DataFrame(pd.read_csv(dpath+files[i]))
    IF=data.loc[:,'IF']
    vidx=IF[IF==1]
    time=data['time'][IF==1]
    P=data['P'][IF==1]
    T=data['T_new'][IF==1]
    RH=data['RH_new'][IF==1]
    LAT=data['LAT'][IF==1]
    LON=data['LON'][IF==1]
    WD=data['WD'][IF==1]
    WS=data['WS'][IF==1]

    logfile_full_path='../test/L0/log.txt'
    
    #filename=files[i].replace('L3','L3pr')
    filename='L3pr.csv'
    opfile = open(opath+filename, "w",newline='\n')

    csv2asp(vidx,time,P,T,RH,LAT,LON,WD,WS,logfile_full_path,opfile)
    
    opfile.close()
