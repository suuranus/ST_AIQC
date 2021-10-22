# This program calculates the specific humidity (q) and standard q with pressure, temperature and relative humidity

import numpy as np

def rh_to_q(p,t,rh):
    epsilon=0.622
    Lv=2.45e+06 #unit: J/kg
    Ls=2.834e+06 #unit: J/kg
    Rv=465.52 #unit: J/(kg*K)

    es=np.zeros(len(rh))

    for i in range(len(rh)):
        if t[i]<0.:
           es[i]=6.11*np.exp((Ls/Rv)*((1/273.15)-(1/(t[i]+273.15))))
        else:
           es[i]=6.11*np.exp((Lv/Rv)*((1/273.15)-(1/(t[i]+273.15))))

    e=es*(rh/100.)
    q=epsilon*(e/p)*1000.

    # # Standard q at T=40 degC, RH=100%
    es0=6.11*np.exp((Lv/Rv)*((1/273.15)-(1/(40.+273.15))))
    e0=es0*1.
    q0=epsilon*(e0/p)*1000.

    return q,q0

def q_to_rh(p,t,q):
    epsilon=0.622
    Lv=2.45e+06 #unit: J/kg
    Ls=2.834e+06 #unit: J/kg
    Rv=465.52 #unit: J/(kg*K)

    es=np.zeros([len(t)])

    for i in range(len(t)):
        if t[i]<0.:
           es[i]=6.11*np.exp((Ls/Rv)*((1/273.15)-(1/(t[i]+273.15))))
        else:
           es[i]=6.11*np.exp((Lv/Rv)*((1/273.15)-(1/(t[i]+273.15))))

    e=((q/1000.)/epsilon)*p
    rh=(e/es)*100.
    rh[rh>100.]=100.
    rh[rh<0.]=0.

    return rh
