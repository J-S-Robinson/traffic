# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 22:27:27 2017

@author: jrobinson47
"""

import xml.etree.ElementTree as ET

def match_routes(rou1, rou2):
    rou3 = rou2
    rou1 = rou1.split(' ')
    rou1 = list(map (lambda x: x.split('_'), rou1))
    rou2 = rou2.split(' ')
    rou2 = list(map (lambda x: x.split('_'), rou2))
    for i in range(len(rou1)):
        if rou1[i][1] == rou2[0][0]:
            rou3 = rou1[0:i+1] + rou2
            for i in range(len(rou3)):
                rou3[i] = '_'.join(rou3[i])
            rou3 = ' '.join(rou3)
            return rou3
    return rou3

def update_state_routes(statefile,routefile,new_statefile):
    #THIS IS TERRIBLE
    state = ET.parse(statefile)
    # first dict ids to routes
    state_el = state.getroot()
    veh2route = {}
    for vehicle in state_el.iter(tag = 'vehicle'):
        veh2route[vehicle.attrib['id']] = vehicle.attrib['route']
    
    routes = ET.parse(routefile)
    
    id2edges = {}
    for vehicle in routes.iter(tag='vehicle'):
        route_def = vehicle.find('route').attrib['edges']
        # set route in state to route_def
        if vehicle.attrib['id'] in veh2route:
            id2edges[veh2route[vehicle.attrib['id']]] = route_def
            
    #state.write('data\\state_test.xml')
    #
    #ROT.start_instance()
    
    with open(statefile) as st_f:
        lines = st_f.readlines()
             
    with open(new_statefile, 'w+') as f:
        for line in lines:
            pline = line
            if '<route' in line:
                temp_el = ET.fromstring(line)
                if temp_el.tag == 'route':
                    if temp_el.attrib['id'] in id2edges:
                        temp_el.set('edges',
                                    match_routes(temp_el.attrib['edges'],
                                                 id2edges[temp_el.attrib['id']]))
                        pline = '    ' + ET.tostring(temp_el,encoding="unicode") + '\n'
            print(pline, end='', file=f)
            
    return