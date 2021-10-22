"""
these funtions are design for caculate the clear sky solar radiation
by the given date, lontitude and latitude

operate by the following step
1.julian_day > transform date into the day of the year [1-365]
2.hour_angle > caculate te hour angle for the particular locaion and time
3.solar > caculating the solar radiation value

@author: Min Lun Wu
"""

# %% module setup
import numpy as np
import pandas as pd
import datetime as dt
from numpy import sin, cos, tan, pi, abs, arccos


# %% julian day
def julian_day(yyyy,mm,dd):
    date_list=pd.to_datetime(yyyy+mm+dd,format='%Y%m%d')
    jd=date_list.apply(lambda x: int(x.strftime('%j')))
    # jd=np.array(date_list.strftime("%j")).astype('int')
    
    return jd

# %% hour angle
def hour_angle(jd,lt,lat,lon):
    rlat=(lat/180)*pi
    gamma=2*pi*(jd-1)/365
    delta=0.006918-0.399912*cos(gamma)+0.070257*sin(gamma)-\
                   0.006758*cos(2*gamma)+0.000907*sin(2*gamma)-\
                   0.002697*cos(3*gamma)+0.00148*sin(3*gamma)

    if abs(tan(rlat)*tan(delta)) >=1:
        if rlat*delta >0:
            hs=pi
        else:
            hs=0
    else:
        hs=arccos(-tan(rlat)*tan(delta))
        
    et=(0.000075+0.001868*cos(gamma)-0.032077*sin(gamma)-\
                0.014615*cos(2*gamma)-0.04089*sin(2*gamma))*229.18
    lst=lt+(4*(lon-120.)+et)/60  # time correction
    hra=(15*(12-lst))
    
    if abs(hs)>0:
        if hs==pi:
            h=pi
        else:
            h=hra
    else:
        h=0
        
    return h

# %% solar radiation
def solar(yyyy,mm,dd,lt,lat,lon):
    
    jd=julian_day(yyyy,mm,dd)
    rlat=(lat/180)*pi
    S0=1370
    rad=np.empty([len(jd)],dtype='float')
    
    for i in range(len(jd)):
        dis=1+0.033*cos(2*pi*(jd[i]/365))
        S=S0*dis
        gamma=2*pi*(jd[i]-1)/365
        delta=0.006918-0.399912*cos(gamma)+0.070257*sin(gamma)-\
                       0.006758*cos(2*gamma)+0.000907*sin(2*gamma)-\
                       0.002697*cos(3*gamma)+0.00148*sin(3*gamma)
                       
        h=hour_angle(jd[i],lt[i],lat[i],lon[i])
        coszen=sin(rlat[i])*sin(delta)+cos(rlat[i])*cos(delta)*cos(h*pi/180);
        if coszen>0:
           rad[i]=S*coszen
        else:
           rad[i]=0
                               
    return rad

# %%