"""
@author: Min Lun Wu
"""
import numpy as np
import datetime as dt

# %%
def mkeol(data,opfile,level,project_name='unknown',site='unknown',lon='unknown',lat='unknown',alt='unknown',ST_id='unknown'):

    duration=data['duration']
    time=data['time'].apply(lambda x: dt.datetime.strptime(x,'%Y-%m-%d %H:%M:%S.%f'))
    launchtime=time[duration==0]
    operation_time=(dt.datetime.now()-dt.timedelta(hours=8)).strftime('%d %b %Y %H:%M')
# %%
    data['time']=data['time'].apply(lambda x: dt.datetime.strptime(x,'%Y-%m-%d %H:%M:%S.%f').strftime('%H %M %S.%f')[:-4])

# %%
    opfile.write('Data Type/Direction:                       StormTracker/Ascending\n')
    opfile.write('File Format/Version:                       EOL Sounding Format/1.1\n')
    opfile.write('Project Name/Platform:                     '+str(project_name)+'/StormTracker\n')
    opfile.write('Launch Site:                               '+str(site)+'\n')
    opfile.write('Launch Location (lon,lat,alt):             '+str(lon)+', '+str(lat)+', '+str(alt)+'\n')
    opfile.write('UTC Launch Time (y,m,d,h,m,s):             '+launchtime[0].strftime('%Y, %m, %d, %H:%M:%S')+'\n')
    opfile.write('Sonde Id/Sonde Type:                       '+str(ST_id)+'/StormTracker/\n')
    opfile.write('Reference Launch Data Source/Time:         unknown/unknown\n')
    opfile.write('System Operator/Comments:                  SOUNDING IN EOL FORMAT/\n')
    opfile.write('Post Processing Comments:                  AIQC_process_v2_L'+str(level)+'; Created on '+operation_time+' UTC  \n')
    opfile.write('/\n')

    opfile.write('  Time   -- UTC  --   Press    Temp   Dewpt    RH     Uwind   Vwind   Wspd     Dir     dZ    GeoPoAlt     Lon         Lat      GPSAlt \n')
    opfile.write('   sec   hh mm   ss     mb      C       C       %      m/s     m/s     m/s     deg     m/s       m        deg         deg         m   \n')
    opfile.write('-------- -- -- ----- ------- ------- ------- ------- ------- ------- ------- ------- ------- -------- ----------- ----------- --------\n')
        
    np.savetxt(opfile,data.values, fmt='%8.2f %s %7.2f %7.2f %7.2f %7.2f %7.2f %7.2f %7.2f %7.2f %7.2f %8.0f %11.6f %11.6f %8.2f ')
    opfile.close()

    return opfile

