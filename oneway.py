# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 01:53:49 2017

@author: Harvey
"""

from utils.network import Network, Edge, Node
from utils.traffic import Vehicle, VehicleType, Route, Demand
import numpy.random as random
import os

from DUAGawron import runDUAGawron

#import duaIterate3

nodes = [Node('0', 0, -1000),
        Node('1', 0, 100),
        Node('2', -50, 150),
        Node('3', 50, 150),
        Node('4', -50, 175),
        Node('5', 50, 175),
        Node('6', 0, 225),
        Node('7', 0, 250)]
        
edges = [Edge(nodes[0],nodes[1]),
         Edge(nodes[1],nodes[2]),
         Edge(nodes[1],nodes[3]),
         Edge(nodes[2],nodes[4],speed=5),
         Edge(nodes[3],nodes[5],speed=2),
         Edge(nodes[4],nodes[6]),
         Edge(nodes[5],nodes[6]),
         Edge(nodes[6],nodes[7],numLanes=2)]
         
newNet = Network(nodes,edges)

sumo_path = 'C:\\dev\\Traffic\\Sumo\\bin'

os.makedirs('oneway_data',exist_ok=True)
newNet.writeNet(sumo_path,'oneway_data\\oneway')

vehTypes = []
vehTypes.append(VehicleType((0,1,0),'smart'))
vehTypes.append(VehicleType((1,0,0),'dumb'))

numCars = 100
starts = Demand._def_rand_departs(numCars,2)
prob_smart = .5
vehicles = []

dumbcars = []
for x in [('%s' % i, random.rand(), starts[i]) for i in range(numCars)]:
    if x[1] < prob_smart:
        vType = vehTypes[0]
    else:
        vType = vehTypes[1]
        dumbcars.append(x[0])
    route = Route(['0_1', '1_3', '3_5', '5_6', '6_7'])    
    vehicles.append(Vehicle(x[0],x[2],vType,route))
dem = Demand(vehTypes,vehicles)

dem.genRouteFile('oneway_data\\oneway.rou.xml')

numiters = 10
print(dumbcars)

runDUAGawron(sumo_path + '\\sumo.exe', sumo_path + '\\duarouter.exe', 'oneway_data\\oneway.net.xml', 'oneway_data\\oneway.rou.xml',
                 numIters=15,folder='DUA_data')
