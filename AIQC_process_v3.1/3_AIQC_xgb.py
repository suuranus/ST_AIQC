import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os, pickle, argparse
import sys
from rh2q import rh_to_q, q_to_rh
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from xgboost import XGBRegressor
from xgboost import plot_importance
import matplotlib.pyplot as plt
from matplotlib import rc
import statsmodels.api as sm
import json
from rh2td import rh2td
from geo_height import geo_height
from mkEOL import mkeol

def stat(p,data):
    mean_all=np.mean(data, axis=0)
    std_all=np.std(data, axis=0)

    mean=np.zeros(7)
    std=np.zeros(7)
    mask=np.zeros(len(data))

    for i in range(7):
        ptmp=p
        tmp=data[ptmp>(1000-100*i-100)]
        ptmp=ptmp[ptmp>(1000-100*i-100)]
        tmp1=tmp[ptmp<=(1000-100*i)]
        mean[i]=np.mean(tmp1)
        std[i]=np.std(tmp1)

    return mean, std, mean_all, std_all

def load_data(f):
    #for root, dirs, files in os.walk(path):
    #    for f in sorted(files):
            if f.endswith('.csv'):
               if os.path.isfile(f):
                  print(f)
                  strs=f.split('_')
                  #print(strs)
                  # ymdh=strs[5]+strs[6][0:4]
                  #ymdh=strs[2]+strs[3]
                  #print(ymdh)
                  #quit()

                  inf=pd.read_csv(f)
                  print(inf.shape)

                  t=inf['T'].values.astype('float')
                  t[t<-50.]=np.nan
                  t[t>50.]=np.nan
                  t[t==-46.85]=np.nan
                  t[t==40.99]=np.nan
                  t[t==-9999.]=np.nan

                  p=inf['P'].values
                  p[p==0.]=np.nan
                  p[p==-9999.]=np.nan

                  rad=inf['rad'].values.astype('float')
                  rad[rad==-9999.]=np.nan

                  rh=inf['RH'].values.astype('float')
                  rh[rh>100.]=100.
                  rh[rh<0.]=np.nan

                  q=inf['q'].values.astype('float')
                  q[q<0.]=np.nan

                  q1,qs=rh_to_q(p,t,rh) # qs, standard q at RH=100%, T=40

                  u=inf['U'].values.astype('float')
                  u[u==-9999.]=np.nan
                  v=inf['V'].values
                  v[v==-9999.]=np.nan

                  for root, dirs, files in os.walk('./L0/'):
                      f_ori=files
                  
                  if len(rh[np.isnan(rh)==True])==0:
                     if len(u[np.isnan(u)==True])==0:
                        switch=0
                        with open('all_log.txt','a') as fout:
                             fout.write(str(f_ori)+"\n")
                     else:
                        switch=1
                        with open('noUV.txt','a') as fout:
                             fout.write(str(f_ori)+"\n")
                  else:
                     if len(u[np.isnan(u)==True])==0:
                        switch=2
                        with open('noRh.txt','a') as fout:
                             fout.write(str(f_ori)+"\n")
                     else:
                        switch=3
                        with open('noUVRh.txt','a') as fout:
                             fout.write(str(f_ori)+"\n")

                  x=pd.DataFrame()
                  x.insert(0,'P',p,True)
                  x.insert(1,'T',t,True)
                  x.insert(2,'RH',rh,True)
                  x.insert(3,'rad',rad,True)
                  x.insert(4,'q',q,True)
                  x.insert(5,'qs',qs,True)
                  x.insert(6,'U',u,True)
                  x.insert(7,'V',v,True)

            return inf,switch, x

def predict(switch,inputs):

    p=inputs['P'].values
    t=inputs['T'].values
    rh=inputs['RH'].values
    rad=inputs['rad'].values
    u=inputs['U'].values
    v=inputs['V'].values
    q=inputs['q'].values
    qs=inputs['qs'].values

    # Mask out
    mask=np.zeros(len(inputs))
    for i in range(len(mask)):
        if np.isnan(p[i])==False and np.isnan(t[i])==False and np.isnan(rh[i])==False and np.isnan(u[i])==False and np.isnan(v[i])==False and np.isnan(rad[i])==False and np.isnan(q[i])==False and np.isnan(qs[i])==False:
          mask[i]+=1

    n_valid=len(mask[mask==1]) # number of non-missing value

    val_p=p[mask==1]
    val_t=t[mask==1]
    val_u=u[mask==1]
    val_v=v[mask==1]
    val_rh=rh[mask==1]
    val_rad=rad[mask==1]
    val_q=q[mask==1]
    val_qs=qs[mask==1]

    if switch==0: # no missing data
       xt=pd.DataFrame()
       xt.insert(0,'P',(val_p/1100.),True)
       xt.insert(1,'T',((val_t-(-50.))/100.),True)
       xt.insert(2,'RH',(val_rh/100.),True)
       xt.insert(3,'U',((val_u-(-50.))/100.),True)
       xt.insert(4,'V',((val_v-(-50.))/100.),True)
       xt.insert(5,'rad',(val_rad/1400.),True)

       print('===== Load GBM-T model with all vars. =====')
       xgb_t=XGBRegressor()
       xgb_t.load_model('T_xgb_tasse_yl_su.json')

       xgb_pred1=xgb_t.predict(xt) # predicting delta-T
       xgb_t_pred=val_t+xgb_pred1 # calculate predicted T

       xgb_t_pred_new=np.zeros(len(p))
       xgb_t_pred_new[mask==0]=np.nan

       count=0
       for i in range(len(p)):
           if xgb_t_pred_new[i]==0.:
              xgb_t_pred_new[i]=xgb_t_pred_new[i]+xgb_t_pred[count]
              count+=1

       xq=pd.DataFrame()
       xq.insert(0,'P',(val_p/1100.),True)
       xq.insert(1,'XGB_T',((xgb_t_pred-(-50.))/100.),True)
       xq.insert(2,'XGB_dt',xgb_pred1,True)
       xq.insert(3,'RH',(val_rh/100.),True)
       xq.insert(4,'U',((val_u-(-50.))/100.),True)
       xq.insert(5,'V',((val_v-(-50.))/100.),True)
       xq.insert(6,'Q',(val_q/val_qs),True)
       xq.insert(7,'rad',(val_rad/1400.),True)

       print('===== Load the GBM-Q model with all vars. =====')
       xgb_q=XGBRegressor()
       xgb_q.load_model('Q_xgb_tasse_yl_su.json')

       xgb_pred2=xgb_q.predict(xq) # Predicting delta-q
       xgb_q_pred=val_q+xgb_pred2 # Calculate predicted q
       xgb_q_pred[xgb_q_pred<0.]=0.

       xgb_q_pred_new=np.zeros(len(p))
       xgb_q_pred_new[mask==0]=np.nan

       xgb_rh_pred=q_to_rh(p,xgb_t_pred,xgb_q_pred)
       xgb_rh_pred_new=np.zeros(len(p))
       xgb_rh_pred_new[mask==0]=np.nan

       xgb_td=rh2td(xgb_t_pred,xgb_rh_pred)
       xgb_td_new=np.zeros(len(p))
       xgb_td_new[mask==0]=np.nan

       count=0
       for i in range(len(p)):
           if xgb_q_pred_new[i]==0.:
              xgb_q_pred_new[i]=xgb_q_pred_new[i]+xgb_q_pred[count]
              xgb_rh_pred_new[i]=xgb_rh_pred_new[i]+xgb_rh_pred[count]
              xgb_td_new[i]=xgb_td_new[i]+xgb_td[count]
              count+=1
   
    if switch==1:
       xt=pd.DataFrame()
       xt.insert(0,'P',(val_p/1100.),True)
       xt.insert(1,'T',((val_t-(-50.))/100.),True)
       xt.insert(2,'RH',(val_rh/100.),True)     
       xt.insert(3,'rad',(val_rad/1400.),True)
       
       print('===== Load GBM-T model without UV =====')
       xgb_t=XGBRegressor()
       xgb_t.load_model('T_xgb_noUV_tasse_yl_su.json')

       xgb_pred1=xgb_t.predict(xt) # predicting delta-T
       xgb_t_pred=val_t+xgb_pred1 # calculate predicted T

       xgb_t_pred_new=np.zeros(len(p))
       xgb_t_pred_new[mask==0]=np.nan

       count=0
       for i in range(len(p)):
           if xgb_t_pred_new[i]==0.:
              xgb_t_pred_new[i]=xgb_t_pred_new[i]+xgb_t_pred[count]
              count+=1
              
       xq=pd.DataFrame()
       xq.insert(0,'P',(val_p/1100.),True)
       xq.insert(1,'XGB_T',((xgb_t_pred-(-50.))/100.),True)
       xq.insert(2,'XGB_dt',xgb_pred1,True)
       xq.insert(3,'RH',(val_rh/100.),True)
       xq.insert(4,'Q',(val_q/val_qs),True)
       xq.insert(5,'rad',(val_rad/1400.),True)

       print('===== Load the GBM-Q model without UV =====')
       xgb_q=XGBRegressor()
       xgb_q.load_model('Q_xgb_noUV_tasse_yl_su.json')

       xgb_pred2=xgb_q.predict(xq) # Predicting delta-q
       xgb_q_pred=val_q+xgb_pred2 # Calculate predicted q
       xgb_q_pred[xgb_q_pred<0]=0.

       xgb_q_pred_new=np.zeros(len(p))
       xgb_q_pred_new[mask==0]=np.nan

       xgb_rh_pred=q_to_rh(p,xgb_t_pred,xgb_q_pred)
       xgb_rh_pred_new=np.zeros(len(p))
       xgb_rh_pred_new[mask==0]=np.nan

       xgb_td=rh2td(xgb_t_pred,xgb_rh_pred)
       xgb_td_new=np.zeros(len(p))
       xgb_td_new[mask==0]=np.nan

       count=0
       for i in range(len(p)):
           if xgb_q_pred_new[i]==0.:
              xgb_q_pred_new[i]=xgb_q_pred_new[i]+xgb_q_pred[count]
              xgb_rh_pred_new[i]=xgb_rh_pred_new[i]+xgb_rh_pred[count]
              xgb_td_pred_new[i]=xgb_td_pred_new[i]+xgb_td_pred[count]
              count+=1
       
    if switch==2:
       xt=pd.DataFrame()
       xt.insert(0,'P',(val_p/1100.),True)
       xt.insert(1,'T',((val_t-(-50.))/100.),True)
       xt.insert(2,'U',((val_u-(-50.))/100.),True)
       xt.insert(3,'V',((val_v-(-50.))/100.),True)
       xt.insert(4,'rad',(val_rad/1400.),True)

       print('===== Load GLM-T_noRH model with UV =====')
       with open('T_xgb_noRh.pkl','rb') as fin:
            xgb_norh=pickle.load(fin)

       xgb_pred3=xgb_norh.predict(xt)
       xgb_t_pred=val_t+xgb_pred3

       xgb_pred3=xgb_norh.predict(xt)
       xgb_t_pred=val_t+xgb_pred3

       xgb_t_pred_new=np.zeros(len(p))
       xgb_t_pred_new[mask==0]=np.nan
       xgb_q_pred_new=np.zeros(len(p))
       xgb_q_pred_new=np.nan
       xgb_rh_pred_new=np.zeros(len(p))
       xgb_rh_pred_new=np.nan
       xgb_td_pred_new=np.zeros(len(p))
       xgb_td_pred_new=np.nan

       count=0
       for i in range(len(p)):
           if xgb_t_pred_new[i]==0.:
              xgb_t_pred_new[i]=xgb_t_pred_new[i]+xgb_t_pred[count]
              count+=1
 
    if switch==3:
       xt=pd.DataFrame()
       xt.insert(0,'P',(val_p/1100.),True)
       xt.insert(1,'T',((val_t-(-50.))/100.),True)
       xt.insert(2,'rad',(val_rad/1400.),True)
       
       print('===== Load GLM-T_noRH model without UV =====')
       with open('T_xgb_noUVRh.pkl','rb') as fin:
            xgb_norh=pickle.load(fin)

       xgb_pred3=xgb_norh.predict(xt)
       xgb_t_pred=val_t+xgb_pred3

       xgb_t_pred_new=np.zeros(len(p))
       xgb_t_pred_new[mask==0]=np.nan
       xgb_q_pred_new=np.zeros(len(p))
       xgb_q_pred_new=np.nan
       xgb_rh_pred_new=np.zeros(len(p))
       xgb_rh_pred_new=np.nan
       xgb_td_pred_new=np.zeros(len(p))
       xgb_td_pred_new=np.nan

       count=0
       for i in range(len(p)):
           if xgb_t_pred_new[i]==0.:
              xgb_t_pred_new[i]=xgb_t_pred_new[i]+xgb_t_pred[count]
              count+=1
       
    return n_valid, val_p, xgb_t_pred,xgb_t_pred_new, xgb_q_pred, xgb_q_pred_new, xgb_rh_pred,xgb_rh_pred_new, xgb_td_new


def main():
    # %%
    # parser = argparse.ArgumentParser(description='Read in stormtracker L2 data in csv format.')
    # parser.add_argument('-d','--datapath', help='The path of ST L2 data.')
    # parser.add_argument('-o', '--outpath', help='The target path of output data.')
    # args=parser.parse_args()

    path='./L2/'
    path_to='./L3/'
    f=sys.argv[1]
    # if args.datapath==None or args.outpath==None:
    #    print('===== Failure =====')
    #    print('Usage: python AIQC.py -d L2_datapath/ -o L3_outpath/')
    #    quit()

    # Read new ST observation data
    for root, dirs, files in os.walk(path): 
#        for f in sorted(files):
            if os.path.isfile(path+f):
               fname=path+f
               opfname=f.replace('L2','L3')
               inf, switch, inputs=load_data(fname)
               tstamp=inf['time']
               lon=inf['LON'].values.astype('float')
               lat=inf['LAT'].values.astype('float')
               duration=inf['duration']
               GPS_Z=inf['GPS_Z']
               P_cac=inf['P'] # original P
               T_cac=inf['T'] # original T
               llh=GPS_Z[duration==0]
               llp=P_cac[duration==0]
               if len(llh)>1:
                  llh=llh[len(llh)-1]
                  llp=llp[len(llp)-1]
 
               n_valid,val_p, xgb_t_pred, xgb_t_pred_new, xgb_q_pred, xgb_q_pred_new, xgb_rh_pred, xgb_rh_pred_new,xgb_td_new=predict(switch, inputs)
               
               if switch<2:
                  
                  print('===== END OF AIQC =====')
                  
                  # Statistics
                  xgb_t_pred_mean, xgb_t_pred_std, xgb_t_pred_mean_all, xgb_t_pred_std_all=stat(val_p, xgb_t_pred)
                  xgb_q_pred_mean, xgb_q_pred_std, xgb_q_pred_mean_all, xgb_q_pred_std_all=stat(val_p, xgb_q_pred)
                  xgb_rh_pred_mean, xgb_rh_pred_std, xgb_rh_pred_mean_all, xgb_rh_pred_std_all=stat(val_p, xgb_rh_pred)

                  #Td_new=pd.Series(rh2td(xgb_t_pred_new,xgb_rh_pred_new))
                  geo_Z_new=pd.Series(geo_height(llh,P_cac,T_cac,llp))
                  dZ_new=geo_Z_new.diff()
                  dZ_new[0]=0.0
                  
                  inf.insert(4,'T_new',xgb_t_pred_new,True)
                  inf.insert(6,'Td_new',xgb_td_new,True)
                  inf.insert(8,'RH_new',xgb_rh_pred_new,True)       
                  inf.insert(14,'dZ_new',dZ_new,True)
                  inf.insert(16,'geoALT_new',geo_Z_new,True)
                  inf.insert(21,'q_new',xgb_q_pred_new,True)

                  inf.to_csv(path_to+opfname, index=False, na_rep='-999.99')

                  with open(path_to+opfname.replace('.csv','_log.txt'),'w') as logf:
                       logf.write('Number of valid data:%s\n' % str(n_valid) )
                       logf.write('Delta-T mean:%s\n' % str(xgb_t_pred_mean_all) )
                       logf.write('Delta-T standard deviation:%s\n' % str(xgb_t_pred_std_all) )
                       logf.write('Delta-q mean:%s\n' % str(xgb_q_pred_mean_all) )
                       logf.write('Delta-q standard deviation:%s\n' % str(xgb_q_pred_std_all) )
                       logf.write('Delta-RH mean:%s\n' % str(xgb_rh_pred_mean_all) )
                       logf.write('Delta-RH standard deviation:%s\n' % str(xgb_rh_pred_std_all) )
                       logf.write('P delta-T dalta-Q delta-RH\n')

                       for i in range(7):
                           lines=str(int(1000-100*i))+'-'+str(int(1000-100*i+100))+' '+str(xgb_t_pred_mean[i])+' '+str(xgb_q_pred_mean[i])+' '+str(xgb_rh_pred_mean[i])
                           logf.write('%s\n'%lines)  
                           
               else:
                  
                  print('===== END OF AIQC =====')

                  # Statistics
                  xgb_t_norh_pred_mean, xgb_t_norh_pred_std, xgb_t_norh_pred_mean_all, xgb_t_norh_pred_std_all=stat(val_p, xgb_t_pred)
                  #Td_new=pd.Series(rh2td(xgb_t_pred_new,xgb_rh_pred_new))
                  geo_Z_new=pd.Series(geo_height(llh,P_cac,T_cac,llp))
                  dZ_new=geo_Z_new.diff()
                  dZ_new[0]=0.0
                  
                  inf.insert(4,'T_new',xgb_t_pred_new,True)
                  inf.insert(6,'Td_new',xgb_td_new,True)
                  inf.insert(8,'RH_new',xgb_rh_pred_new,True)       
                  inf.insert(14,'dZ_new',dZ_new,True)
                  inf.insert(16,'geoALT_new',geo_Z_new,True)
                  inf.insert(21,'q_new',xgb_q_pred_new,True)
                  
                  inf.to_csv(path_to+opfname, index=False, na_rep='-999.99')

                  #with open(path_to+'L3_'+ymdh+'.txt','w') as logf:
                  with open(path_to+opfname.replace('.csv','_log.txt'),'w') as logf:
                       logf.write('Number of valid data:%s\n' % str(n_valid) )
                       logf.write('Delta-T mean:%s\n' % str(xgb_t_norh_pred_mean_all) )
                       logf.write('Delta-T standard deviation:%s\n' % str(xgb_t_norh_pred_std_all) )
                       logf.write('P delta-T\n')
                       for i in range(7):
                           lines=str(int(1000-100*i))+'-'+str(int(1000-100*i+100))+' '+str(xgb_t_norh_pred_mean[i])
                           logf.write('%s\n'%lines)
                           
    # Rearrange to eol format                       
    EOLdpath='./L3/'
    EOLopath='./L3/'

    if os.path.isfile(EOLdpath+opfname):
        data=[]
        data=pd.DataFrame(pd.read_csv(EOLdpath+opfname))
        launch_info=data.iloc[1,:]

        eol_data=data.loc[:,['duration','time','P','T','Td','RH','U','V','WS','WD','dZ','geoALT','LON','LAT','GPS_Z']].reset_index(drop=True)
        eol_data.columns=['duration','time','P','T','Td','RH','U','V','WS','WD','dZ','geoALT','LON','LAT','GPS_Z']

        EOL_filename=opfname.replace('.csv','.eol')
        EOLopfile = open(EOLopath+EOL_filename, "w",newline='\n')
        mkeol(eol_data,EOLopfile,'2',lon=launch_info['LON'],lat=launch_info['LAT'],alt=launch_info['GPS_Z'])
        EOLopfile.close()

# %%
if __name__=='__main__':
    main()
   
