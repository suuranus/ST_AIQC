"""
@author: Min Lun Wu
 calculates the hydrostatic height
 input unit P(hPa) T(deg C) P_ground(hPa)
"""
import numpy as np

def geo_height(h_ground,P,T,P_ground):
    R = 287	    # gas constant
    g = 9.81 	# m/s^2
    k0=273.15
    hh=np.zeros(len(P))
    
    for i in range(len(P)):     
        hh[i] = -1*(R/g)*(T[i]+k0)*np.log(P[i]/P_ground)+h_ground
        
    return hh