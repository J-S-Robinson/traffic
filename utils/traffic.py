# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 12:19:08 2017

@author: jrobinson47
"""

from numpy import random
import xml.etree.ElementTree as ET

class VehicleType:
    
    def __init__(self,color,ID):
        self.color = color
        self.ID = ID
        
    def get_XML_Element(self):
        return ET.Element('vType', 
                   attrib={'color':','.join(str(x) for x in self.color),
                           'id':self.ID})
        
class Vehicle:
    
    def __init__(self,ID,departTime,vType,route,departSpeed=15,departLane='free'):
        self.ID = ID
        self.departTime = departTime
        self.departSpeed = departSpeed
        self.departLane = departLane
        self.route = route
        self.vType = vType
        
    def get_XML_Element(self):
        vehElem = ET.Element('vehicle',
                          attrib={'id':self.ID,
                                  'depart':'%s' % self.departTime,
                                  'departLane': '%s' % self.departLane,
                                  'departSpeed': '%s' % self.departSpeed,
                                  'departPos': 'last',
                                  'type':self.vType.ID})
        vehElem.append(self.route.get_XML_Element())
        return vehElem

class Route:
    
    def __init__(self,edges):
        self.edges = edges
        
    def get_XML_Element(self):
        return ET.Element('route',
                          attrib={'edges': ' '.join(self.edges)})
        
class Demand:
    
    def __init__(self,vTypes,vehicles):
        self.vTypes = vTypes
        self.vehicles = vehicles
    
    def _def_rand_departs(n, avg_interval, min_interval=False):
        t = [None] * n
        t[0] = random.exponential(scale=avg_interval)
        for i in range(1,n):
            interval = random.exponential(scale=avg_interval)
            if min_interval:
                if interval < min_interval:
                    interval = min_interval
            t[i] = t[i-1] + interval
        return t
        
    def genRouteFile(self,out):
        routeRoot = ET.Element('routes')
        for vType in self.vTypes:
            new_vType = vType.get_XML_Element()
            routeRoot.append(new_vType)
        for vehicle in self.vehicles:
            new_veh = vehicle.get_XML_Element()
            routeRoot.append(new_veh)
        routeTree = ET.ElementTree()
        routeTree._setroot(routeRoot)
        routeTree.write(out)