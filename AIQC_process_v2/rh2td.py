"""
@author: Min Lun Wu
"""
import numpy as np

def rh2td(T,RH):    
    a1=17.625
    b1=243.04
    aa=np.zeros(len(T))
    bb=np.zeros(len(T))
    
    for i in range(len(T)):       
        bb[i]=b1*(np.log(RH[i]/100)+(a1*T[i]/(b1+T[i])))
        aa[i]=a1-np.log(RH[i]/100)-(a1*T[i]/(b1+T[i]))
     
    Td=bb/aa
    return Td