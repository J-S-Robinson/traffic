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
        m = measure(truth)
        # remove some measurements based on probability of detection
        m = [i for i in m if rand() < self.p_d]
        # add Gaussian error to each component of each measurement
        for i in m:
            for j in i:
                i[j] += self.accuracy[j] * gauss(0,1)
                
        
                
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
                f.write('   <inductionLoop id="%s" lane="%s" pos="%s" freq="%s"/\n>'
                        % (s.id, s.lane, s.pos, s.frequency))
            f.write('</additional>')