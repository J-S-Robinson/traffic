# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 13:23:42 2017

@author: jrobinson47
"""
    
def associate_nn(self, belief, measures, gates, time):
    for i in measures:
        #what do we think speed is there
        if i['speed']:
            i['position'] = (i['sensor'].position + 
                i['speed']*(time - i['time']))
        #multiply by current time - measure
        
        nearest = {}
        for j in belief.vehicle.getIDList():
            p_j = belief.vehicle.getPosition(j)
            if i['position'] < p_j + gates[j] and i['position'] > p_j - gates[j]:
                nearest[j] = abs(p_j - i['position'])
        
        if nearest:
            nearest_k = min(nearest, key=nearest.get)
            i['association'] = nearest_k
        else:
            i['association'] = 'new'