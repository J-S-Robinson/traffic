# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 13:56:27 2017

@author: John
"""

import xml.etree.ElementTree as ET

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
        
ti = readTripInfo('C:\\dev\\traffic\\traffic-master\\DUA_data\\tripInfo.xml',
['duration'])

print(ti['1'])
