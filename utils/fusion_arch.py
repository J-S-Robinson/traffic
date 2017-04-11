# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 18:18:29 2017

@author: Harvey
"""
from random import random as rand, gauss

class Sensor:
    # accuracy, misses, false alarms
    # location
    def __init__(self,location, accuracy, p_d, fa=None):
        self.edge = location.edge
        self.position = location.position
        self.lane = location.lane # can this be a list???
        self.accuracy = accuracy
        self.p_d = p_d
        self.fa = fa
        
    def genMeasurements(self, truth, measure, interval):
        # truth is a traci instance of the true traffic state
        # measure is a function which retrieves the measured state from truth
        m = measure(truth)
        # remove some measurements based on probability of detection
        m = [i for i in m if rand() < self.p_d]
        # add Gaussian error to each component of each measurement
        for i in m:
            for j, jj in zip(i,range(len(i))):
                j += self.accuracy[jj] * gauss(0,1)
                
class Association:
    
    def __init__(self,measure,rule):
        pass
        
class FusionArchitecture:
    
    def __init__(self,sensors,fusion_nodes,edges):
        self.sensors = sensors
        self.f_nodes = fusion_nodes
        self.f_edges = edges
        
    def genDetectorFile(self,file):
        pass