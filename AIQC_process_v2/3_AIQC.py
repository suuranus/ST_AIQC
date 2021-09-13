import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os, pickle, argparse
from rh2q import rh_to_q, q_to_rh
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
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
        #np.where((ptmp>(1000-100*i-100)),ptmp,np.nan)
        #np.where((ptmp<=(1000-100*i)),1,np.nan)
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

                  tstamp=inf['time']
                  lon=inf['LON'].values.astype('float')
                  lat=inf['LAT'].values.astype('float')

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

                  if len(rh[np.isnan(rh)==True])==0:
                     switch=0
                  else:
                     switch=1

                  u=inf['U'].values.astype('float')
                  u[u==-9999.]=np.nan
                  v=inf['V'].values
                  v[v==-9999.]=np.nan

                  x=pd.DataFrame()
                  x.insert(0,'P',p,True)
                  x.insert(1,'T',t,True)
                  x.insert(2,'RH',rh,True)
                  x.insert(3,'rad',rad,True)
                  x.insert(4,'q',q,True)
                  x.insert(5,'qs',qs,True)

            #return inf, switch, ymdh, x
            return inf, switch, x

def main():
    # %%
    # parser = argparse.ArgumentParser(description='Read in stormtracker L2 data in csv format.')
    # parser.add_argument('-d','--datapath', help='The path of ST L2 data.')
    # parser.add_argument('-o', '--outpath', help='The target path of output data.')
    # args=parser.parse_args()

    path='./L2/'
    path_to='./L3/'

    # if args.datapath==None or args.outpath==None:
    #    print('===== Failure =====')
    #    print('Usage: python AIQC.py -d L2_datapath/ -o L3_outpath/')
    #    quit()

    # Read new ST observation data
    for root, dirs, files in os.walk(path): 
        for f in sorted(files):
            if f.endswith('.csv'):
               fname=path+f
               # opfname=f.replace('L2','L3')
               #inf, switch, ymdh, inputs=load_data(fname)
               inf, switch, inputs=load_data(fname)
               p=inputs['P'].values
               t=inputs['T'].values
               rh=inputs['RH'].values
               rad=inputs['rad'].values
               q=inputs['q'].values
               qs=inputs['qs'].values
               duration=inf['duration']
               GPS_Z=inf['GPS_Z']
               P_cac=inf['P']
               T_cac=inf['T']
               llh=GPS_Z[duration==0]
               llp=P_cac[duration==0]
               
               # %%
               mask=np.zeros(len(inputs))
               for i in range(len(mask)):
                   if np.isnan(p[i])==False and np.isnan(t[i])==False and np.isnan(rh[i])==False and np.isnan(rad[i])==False and np.isnan(q[i])==False and np.isnan(qs[i])==False:
                      mask[i]+=1

               n_valid=len(mask[mask==1]) # number of non-missing value
               #print(n_valid)

               val_p=p[mask==1]
               val_t=t[mask==1]
               val_rh=rh[mask==1]
               val_rad=rad[mask==1]
               val_q=q[mask==1]
               val_qs=qs[mask==1]

               if switch==0:
                  x=pd.DataFrame()
                  x.insert(0,'P',(val_p/1100.),True)
                  x.insert(1,'T',((val_t-(-50.))/100.),True)
                  x.insert(2,'RH',(val_rh/100.),True)
                  x.insert(3,'rad',(val_rad/1400.),True)
   
                  print('===== Load GLM-T model =====')
                  with open('T_glm_noUV.pkl','rb') as fin:
                       glm_t=pickle.load(fin)

                  glm_pred1=glm_t.predict(x)
                  glm_t_pred=val_t+glm_pred1

                  glm_t_pred_new=np.zeros(len(p))
                  glm_t_pred_new[mask==0]=np.nan

                  count=0
                  for i in range(len(p)):
                      if glm_t_pred_new[i]==0.:
                         glm_t_pred_new[i]=glm_t_pred_new[i]+glm_t_pred[count]
                         count+=1

                  xq=pd.DataFrame()
                  xq.insert(0,'P',(val_p/1100.),True)
                  xq.insert(1,'GLR_T',((glm_t_pred-(-50.))/100.),True)
                  xq.insert(2,'GLR_dt',glm_pred1,True)
                  xq.insert(3,'RH',(val_rh/100.),True)
                  xq.insert(4,'Q',(val_q/val_qs),True)

                  print('===== Load the GLM-Q model =====')
                  with open('Q_glm_noUV.pkl','rb') as fin:
                       glm_q=pickle.load(fin)

                  glm_pred2=glm_q.predict(xq)
                  glm_q_pred=val_q+glm_pred2
   
                  glm_q_pred_new=np.zeros(len(p))
                  glm_q_pred_new[mask==0]=np.nan

                  glm_rh_pred=q_to_rh(p,glm_t_pred,glm_q_pred)
                  glm_rh_pred_new=np.zeros(len(p))
                  glm_rh_pred_new[mask==0]=np.nan

                  count=0
                  for i in range(len(p)):
                      if glm_q_pred_new[i]==0.:
                         glm_q_pred_new[i]=glm_q_pred_new[i]+glm_q_pred[count]
                         glm_rh_pred_new[i]=glm_rh_pred_new[i]+glm_rh_pred[count]
                         count+=1

                  # Statistics
                  glm_t_pred_mean, glm_t_pred_std, glm_t_pred_mean_all, glm_t_pred_std_all=stat(val_p, glm_t_pred)
                  glm_q_pred_mean, glm_q_pred_std, glm_q_pred_mean_all, glm_q_pred_std_all=stat(val_p, glm_q_pred)
                  glm_rh_pred_mean, glm_rh_pred_std, glm_rh_pred_mean_all, glm_rh_pred_std_all=stat(val_p, glm_rh_pred)
                  Td_new=pd.Series(rh2td(glm_t_pred_new,glm_rh_pred_new))
                  geo_Z_new=pd.Series(geo_height(llh,P_cac,T_cac,llp))
                  dZ_new=geo_Z_new.diff()
                  dZ_new[0]=0.0
                  
                  inf.insert(4,'T_new',glm_t_pred_new,True)
                  inf.insert(6,'Td_new',Td_new,True)
                  inf.insert(8,'RH_new',glm_rh_pred_new,True)       
                  inf.insert(14,'dZ_new',dZ_new,True)
                  inf.insert(16,'geoALT_new',geo_Z_new,True)
                  inf.insert(21,'q_new',glm_q_pred_new,True)

                  #inf.to_csv(path_to+opfname, index=Fapytholse, na_rep='-999.99')
                  inf.to_csv(path_to+'L3.csv', index=False, na_rep='-999.99')

                  #with open(path_to+'L3_log_'+ymdh+'.txt','w') as logf:
                  with open(path_to+'L3_log.txt','w') as logf:
                       logf.write('Number of valid data:%s\n' % str(n_valid) )
                       logf.write('Delta-T mean:%s\n' % str(glm_t_pred_mean_all) )
                       logf.write('Delta-T standard deviation:%s\n' % str(glm_t_pred_std_all) )
                       logf.write('Delta-q mean:%s\n' % str(glm_q_pred_mean_all) )
                       logf.write('Delta-q standard deviation:%s\n' % str(glm_q_pred_std_all) )
                       logf.write('Delta-RH mean:%s\n' % str(glm_rh_pred_mean_all) )
                       logf.write('Delta-RH standard deviation:%s\n' % str(glm_rh_pred_std_all) )
                       logf.write('P delta-T dalta-Q delta-RH\n')

                       for i in range(7):
                           lines=str(int(1000-100*i))+'-'+str(int(1000-100*i+100))+' '+str(glm_t_pred_mean[i])+' '+str(glm_q_pred_mean[i])+' '+str(glm_rh_pred_mean[i])
                           logf.write('%s\n'%lines)

               if switch==1:
                  x1=pd.DataFrame()
                  x1.insert(0,'P',(val_p/1100.),True)
                  x1.insert(1,'T',((val_t-(-50.))/100.),True)
                  x1.insert(2,'rad',(val_rad/1400.),True)

                  print('===== Load GLM-T_noRH model =====')
                  with open('T_glm_noUVRh.pkl','rb') as fin:
                       glm_norh=pickle.load(fin)

                  glm_pred3=glm_norh.predict(x1)
                  glm_t_norh_pred=val_t+glm_pred3

                  glm_t_norh_pred_new=np.zeros(len(p))
                  glm_t_norh_pred_new[mask==0]=np.nan
                  glm_q_norh_pred_new=np.zeros(len(p))
                  glm_q_norh_pred_new=np.nan
                  glm_rh_norh_pred_new=np.zeros(len(p))
                  glm_rh_norh_pred_new=np.nan

                  count=0
                  for i in range(len(p)):
                      if glm_t_norh_pred_new[i]==0.:
                         glm_t_norh_pred_new[i]=glm_t_norh_pred_new[i]+glm_t_norh_pred[count]
                         count+=1

                  # Statistics
                  glm_t_norh_pred_mean, glm_t_norh_pred_std, glm_t_norh_pred_mean_all, glm_t_norh_pred_std_all=stat(val_p, glm_t_norh_pred)
                  Td_new=pd.Series(rh2td(glm_t_pred_new,glm_rh_pred_new))
                  geo_Z_new=pd.Series(geo_height(llh,P_cac,T_cac,llp))
                  dZ_new=geo_Z_new.diff()
                  dZ_new[0]=0.0
                  
                  inf.insert(4,'T_new',glm_t_pred_new,True)
                  inf.insert(6,'Td_new',Td_new,True)
                  inf.insert(8,'RH_new',glm_rh_pred_new,True)       
                  inf.insert(14,'dZ_new',dZ_new,True)
                  inf.insert(16,'geoALT_new',geo_Z_new,True)
                  inf.insert(21,'q_new',glm_q_pred_new,True)
                  
                  # inf.to_csv(path_to+'L23_'+ymdh+'.csv', index=False, na_rep='-999.99')
                  #inf.to_csv(path_to+opfname, index=False, na_rep='-999.99')
                  inf.to_csv(path_to+'L3.csv', index=False, na_rep='-999.99')


                  #with open(path_to+'L3_'+ymdh+'.txt','w') as logf:
                  with open(path_to+'L3_log.txt','w') as logf:
                       logf.write('Number of valid data:%s\n' % str(n_valid) )
                       logf.write('Delta-T mean:%s\n' % str(glm_t_norh_pred_mean_all) )
                       logf.write('Delta-T standard deviation:%s\n' % str(glm_t_norh_pred_std_all) )
                       logf.write('P delta-T\n')
                       for i in range(7):
                           lines=str(int(1000-100*i))+'-'+str(int(1000-100*i+100))+' '+str(glm_t_norh_pred_mean[i])
                           logf.write('%s\n'%lines)
                            
             
# %%
if __name__=='__main__':
    main()
    
# %%
dpath='./L3/'
opath='./L3/'
files = [_ for _ in os.listdir(dpath) if _.endswith(".csv")]

for i in range(len(files)):
    data=[]
    data=pd.DataFrame(pd.read_csv(dpath+files[i]))
    launch_info=data.iloc[1,:]
    eol_data=data.loc[:,['duration','time','P','T_new','Td_new','RH_new','U','V','WS','WD','dZ_new','geoALT_new','LON','LAT','GPS_Z']].reset_index(drop=True)
    eol_data.columns=['duration','time','P','T','Td','RH','U','V','WS','WD','dZ','geoALT','LON','LAT','GPS_Z']
    
    # %%
    filename='L3.eol'
    
    opfile = open(opath+filename, "w",newline='\n')
    mkeol(eol_data,opfile,'3',lon=launch_info['LON'],lat=launch_info['LAT'],alt=launch_info['GPS_Z'])
    opfile.close()  