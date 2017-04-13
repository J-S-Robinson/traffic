# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 18:18:29 2017

@author: Harvey
"""
from random import random as rand, gauss

class Sensor:
    # accuracy, misses, false alarms
    # location
    def __init__(self, sensor_id, position, lane, accuracy, p_d, fa=None, freq = 1):
        self.id = sensor_id
        self.position = position
        self.lane = lane # can this be a list???
        self.accuracy = accuracy
        self.p_d = p_d
        self.fa = fa
        self.frequency = freq
        
    def genMeasurements(self, truth, measure):
        # truth is a traci instance of the true traffic state
        # measure is a function which retrieves the measured state from truth
        m = measure(self,truth)
        # remove some measurements based on probability of detection
        if m:
            m = [i for i in m if rand() < self.p_d]
            # add Gaussian error to each component of each measurement
            for i in m:
                i['time'] += self.accuracy[0] * gauss(0,1)
                if i['speed'] and (len(self.accuracy) > 1):
                    i['speed'] += self.accuracy[1] * gauss(0,1)
        return m
    
    def measure_T_and_V(self,truth):
        m = []
        if truth.inductionloop.getLastStepVehicleNumber(self.id) > 0:
            vd = truth.inductionloop.getVehicleData(self.id)
            for v in vd:
                mm = {}
                mm['sensor'] = self.id
                mm['lane'] = truth.inductionloop.getLaneID(self.id)
                mm['time'] = v[2]
                mm['speed'] = truth.inductionloop.getLastStepMeanSpeed(self.id)
                m.append(mm)
        return m
                
class Association:
    
    def __init__(self, belief):
        self.belief = belief
        pass
    
    def associate(self, measures):
        pass
        
class FusionArchitecture:
    
    def __init__(self,sensors,fusion_nodes,edges):
        self.sensors = sensors
        self.f_nodes = fusion_nodes
        self.f_edges = edges
        
    def genDetectorFile(self,file):
        with open(file, 'w+') as f:
            f.write('<additional>\n')
            for s in self.sensors:
                f.write('   <inductionLoop id="%s" lane="%s" pos="%s" freq="%s" file="out.xml"/>\n'
                        % (s.id, s.lane, s.position, s.frequency))
            f.write('</additional>')