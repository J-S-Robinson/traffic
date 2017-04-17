# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 16:08:28 2017

@author: jrobinson47
"""
import os, sys, random
g = os.path.abspath('..')
if g not in sys.path:
    sys.path.append(g)
from utils.network import Network, Edge, Node
from utils.traffic import Vehicle, VehicleType, Route, Demand
import runSim
import utils.fusion_arch as Fusion


def run():
    nodes = [Node('0', 0, 0),
             Node('1', 0, 50),
             Node('2', 0, 400)]
    
    edges = [Edge(nodes[0], nodes[1]),
             Edge(nodes[1], nodes[2])]
    
    newNet = Network(nodes,edges)
    
    
    with open("local\\sumo.path", 'r') as f:
        sumo_path = f.read()
        sumo_tools = sumo_path + '\\tools'
        sumo_path += '\\bin'
        print(sumo_path)
        
    os.makedirs('simple_2d',exist_ok=True)
    newNet.writeNet(sumo_path,'simple_2d\\2d')
        
    vehTypes = []
    vehTypes.append(VehicleType((0,1,0),'smart'))
    vehTypes.append(VehicleType((1,0,0),'dumb'))
    
    numCars = 100
    starts = Demand._def_rand_departs(numCars,2)
    prob_smart = .5
    vehicles = []
    
    dumbcars = []
    for x in [('%s' % i, random.random(), starts[i]) for i in range(numCars)]:
        if x[1] < prob_smart:
            vType = vehTypes[0]
        else:
            vType = vehTypes[1]
            dumbcars.append(x[0])
        route = Route(['0_1', '1_2'])    
        vehicles.append(Vehicle(x[0],x[2],vType,route))
    dem = Demand(vehTypes,vehicles)
    
    dem.genRouteFile('simple_2d\\2d.rou.xml')
    
    sensorList = []
    lane = '1_2_0'
    sensorList.append(Fusion.Sensor('first', 75, lane, [.25], .95))
    sensorList.append(Fusion.Sensor('second', 200, lane, [.25], .95))
    fus = Fusion.FusionArchitecture(sensorList,None,None) 
    
    runSim.runSim('simple_2d\\2d.net.xml','simple_2d\\2d.rou.xml',
           None,fusion=fus)