# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 13:56:27 2017

@author: John
"""

import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np

def readTripInfo(file,keys):
    info = {}
    tree = ET.parse(file)
    for el in tree.findall('tripinfo'):
        temp = {}
        for key in keys:
            temp[key] = el.attrib.get(key)
        info[el.attrib.get('id')] = temp
    return info

def getRelativeTravelTime(info_old,info_new):
    pass
        
ti = readTripInfo('C:\\dev\Traffic_Dev\\DUA_data\\initTripInfo.xml',
['duration'])
tf = readTripInfo('C:\\dev\Traffic_Dev\\DUA_data\\finalTripInfo.xml',
['duration'])

dt = []
for key in ti.keys():
    dt.append(float(ti[key]['duration']) - float(tf[key]['duration']))
plt.hist(dt, bins= np.arange(min(dt), max(dt) + 5, 5))

print(sum(dt)/len(dt))