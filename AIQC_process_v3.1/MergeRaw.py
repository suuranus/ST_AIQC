#-*-coding:utf-8 -*-
import logging
import os
from time import gmtime, strftime, localtime
import math
from math import pi, sqrt, cos, sin, tan, asin, acos, atan
import dateutil.parser
import datetime
from datetime import timedelta
import struct
from multiprocessing.dummy import Pool as ThreadPool 
import concurrent.futures

path_of_Lora_data_to_merge="/home/DATA/stormtracker/KPOP2021/newData/"

data_date = ""
last_date = ""
station_lon = 121.538715
station_lat = 25.014852
station_height = 0
last_ID = -1

def view_params(lat1D, lon1D, alt1, lat2D, lon2D, alt2):
    # Input: lat of observer, lon of observer, altitude(m) of observer
    #        lat of object,   lon of object,   altitude(m) of object
    ## Haversine formula
    ## Vincenty's formulae
    ## Great-circle navigation
    ## World Geodetic System
    R = 6378100 # Radius of Earth (km)
    # Convert degrees to radians
    lat1 = lat1D * pi/180
    lat2 = lat2D * pi/180
    lon1 = lon1D * pi/180
    lon2 = lon2D * pi/180
    # Difference in latitude/longitude
    dLon = lon2 - lon1
    dLat = lat2 - lat1
    # Distance: haversine formula
    h = sin(dLat/2)*sin(dLat/2) + cos(lat1)*cos(lat2)*sin(dLon/2)* sin(dLon/2)
    if h > 1 : h = 1
    d = 2 * R * asin(sqrt(h))
    # Azimuth
    a1 = atan(sin(dLon) / (cos(lat1)*tan(lat2) - sin(lat1)*cos(dLon)))
    if dLat < 0: a1 += pi
    if a1 < 0 : a1 += 2*pi
    # Elevation angle
    lmd = atan( (alt2-alt1)/d )
    # Convert radians to degrees
    a1D = a1 * (180/pi)
    lmdD = lmd * (180/pi)
    return d/1000.0, a1D, lmdD # Distance(km), Azimuth(deg), Elevation angle(deg)


def readdata(data):
    global last_ID
    global station_lat
    global station_lon
    global station_height
    csv = data.split(',')
    try:
        t = dateutil.parser.parse(csv[0])+timedelta(hours=8)
        pass
    except Exception as e:
        print (csv[0])
        return ""
    if last_ID == int(csv[2]):
      return ""
      pass
    last_ID = int(csv[2])
    node_lat = float(csv[8])/100000
    node_lon = float(csv[7])/100000
    node_height = float(csv[9])/100
    sat_count = int(csv[10])
    d = 0
    phi = 0
    lamba = 0
    if station_lat != node_lat and station_lon != node_lon:
      try:
        d,phi,lamba = view_params(station_lat,station_lon,station_height,node_lat,node_lon,node_height)
        pass
      except Exception as e:
        print (e)
      pass
    temp = float(csv[3])/100
    humidity = float(csv[4])/10
    pressure = float(csv[5])/100
    voltage = float(csv[6])/1023*1.1*2
    rssi = float(csv[11])
    speed = float(csv[14])/100
    SNR = int(csv[15])
    Direction = float(csv[16])/100
    ID = int(csv[17])
    #QC
    if rssi > 0:
      rssi = -rssi
      pass
    if len(csv)<11:
      return ""
      pass
    data_str = t.strftime("%Y/%m/%d %H:%M:%S.%f")+","+str(ID)+","+csv[2]+","+str(temp)+","+str(humidity)+","+str(pressure)+","+str(voltage)+","+str(rssi)+","+str(node_lat)+","+str(node_lon)+","+str(node_height)+","+str(d)+","+str(sat_count)+","+str(SNR)+","+str(speed)+","+str(Direction)+","+str(lamba)+"\n"
    return data_str
    pass


def readdata_Gateway(data):
    global last_ID
    t = dateutil.parser.parse(data['Time'])+timedelta(hours=8)
    sat_count =  data['sat_count']
    last_ID = data['ID']
    node_lat = float(data['node_lat'])/100000
    node_lon = float(data['node_lon'])/100000
    node_height = float(data['node_height'])/100
    try:
        d,phi,lamba = view_params(station_lat,station_lon,10,node_lat,node_lon,node_height)
        pass
    except Exception as e:
        print (e)
        print (str(last_ID))
        d = 0
        phi = 0
        lamba = 0
    temp = float(data['temp'])/100
    humidity = float(data['humidity'])/10
    pressure = float(data['pressure'])/100
    voltage = float(data['voltage'])/1023*1.1*2
    rssi =  data['RSSI']
    speed =float(data['speed'])/100
    SNR = data['SNR']
    Direction = float(data['Direction'])/100
    if rssi > 0:
      rssi = -rssi
      pass
    data_str = t.strftime("%Y/%m/%d %H:%M:%S.%f")+","+str(data['NodeNO'])+","+str(data['ID'])+","+str(temp)+","+str(humidity)+","+str(pressure)+","+str(voltage)+","+str(rssi)+","+str(node_lat)+","+str(node_lon)+","+str(node_height)+","+str(d)+","+str(sat_count)+","+str(SNR)+","+str(speed)+","+str(Direction)+","+str(lamba)+"\n"
    return data_str
    pass

import os



#convertString(RawFileList[0])

def convertString(filename):
    Level0_string = []
    print(filename)
    if "LoRa_" in filename:
        data_log = open(filename,'r')
        data = data_log.readlines()
        for line in data:
          try:
            ID = int(line.split(",")[17])
            packageNo = int(line.split(",")[2])
            output = readdata(line) 
            if output != "":
              Level0_string.append(output)
              #print(output)
              pass
            pass
          except Exception as e:
            print (e)
            print (line)
    if "pktlog" in filename:
        data_log = open(filename,'r')
        temp = data_log.readline()
        data = data_log.readlines()
        for line in data:
          try:
            data = line.split(",")
            status = data[7].replace('"',"")
            length = int(data[8])
            if length != 33:
                continue
                pass
            if status != "CRC_OK ":
                #print(status)
                continue
                pass
            raw_binary_str = data[15].replace("-","").replace('"',"").replace('\n',"")
            splited_data = struct.unpack("<HHHhfHlllBHI",bytearray.fromhex(raw_binary_str))
            ID = int(splited_data[1])
            packageNo = int(splited_data[0])
            payload_data = {
                'ID':splited_data[0],
                'NodeNO':splited_data[1],
                'voltage':splited_data[2],
                'temp':splited_data[3],
                'pressure':splited_data[4],
                'humidity':splited_data[5],
                'node_lon':splited_data[6],
                'node_lat':splited_data[7],
                'node_height':splited_data[8],
                'sat_count':splited_data[9],
                'speed':splited_data[10],
                'Direction':splited_data[11],
                'RSSI':float(data[13]),
                'SNR':float(data[14]),
                'Time':data[2].replace('"',"")
            }
            output = readdata_Gateway(payload_data)
            if output != "":
              Level0_string.append(output)
              pass
            pass
          except Exception as e:
            print(e)
            print(line)
    return Level0_string
    pass

def cmp_L0_Data(a, b):
    a_PackageNo = int(a.split(",")[2])
    #a_Time= dateutil.parser.parse(a.split(",")[0])
    b_PackageNo = int(b.split(",")[2])
    #b_Time= dateutil.parser.parse(b.split(",")[0])
    if a_PackageNo > b_PackageNo:
        return 1
    elif a_PackageNo == b_PackageNo:
        return 0
    else:
        return -1

from functools import cmp_to_key
cmp_items_py3 = cmp_to_key(cmp_L0_Data)

def writeL0Data(convertedString):
    if len(convertedString) < 100:
        return
        pass
    channeldata = convertedString
    ID = int(channeldata[0].split(",")[1])
    channeldata = list(set(channeldata))
    channeldata.sort()
    '''
    channeldata_noduplicate = []
    channeldata_noduplicate_PackageID = []
    for line in channeldata:
        if int(line.split(",")[2]) not in channeldata_noduplicate_PackageID:
            channeldata_noduplicate_PackageID.append(int(line.split(",")[2]))
            channeldata_noduplicate.append(line)
            pass
        pass
    channeldata_noduplicate.sort()
    '''
    print("Node %d :%s" % (ID,len(channeldata)))
    f = open(path_of_Lora_data_to_merge+"no_"+str(ID)+".csv",'w')
    f.write("Time,NodeID,PacketID,Temperature(degree C),Humidity(%),Pressure(hPa),Voltage(V),RSSI,Lat,Lon,Height(m),Distance(km),Sat,SNR,Speed(km/hr),Direction(degree),angle(degree)\n")  
    for line in channeldata:
        f.write(line)
    pass

if __name__ ==  '__main__':
    RawFileList = []
    for root, dirs, files in os.walk(path_of_Lora_data_to_merge):
        #print(dirs)
        for filename in files:
            #print(filename)
            #print(os.path.join(root, filename))
            #if filename.startswith("LoRa_") or filename.startswith("pktlog"):
            if "LoRa" in filename:
                RawFileList.append(os.path.join(root, filename))
    channel = [ [] for _ in range(65535)]
    with concurrent.futures.ProcessPoolExecutor(max_workers=3) as executor:
        for Level0_string in executor.map(convertString, RawFileList):
            for line in Level0_string:
                ID = int(line.split(",")[1])
                channel[ID].append(line)
                pass

    print("Writing Data")

    with concurrent.futures.ProcessPoolExecutor(max_workers=3) as executor:
        for Level0_string in executor.map(writeL0Data, channel):
            pass

