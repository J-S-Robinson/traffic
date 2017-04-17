# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 22:27:27 2017

@author: jrobinson47
"""

import xml.etree.ElementTree as ET

# Workaround for traci's inconsistent insertion of vehicles.
# USE WITH CARE
# Expensive call due to file I/O and reloading sumo
# Inserting vehicles can lead to crashes due to vehicles following to close!
def forceUpdateBelief(file,changeVeh = None,addVeh = None,remVeh = None,
                      newFile = None):
    tree = ET.parse(file)
    if changeVeh:
        els = tree.findall('vehicle')
        for veh in changeVeh:
            for i in els:
                if i.get('id') == veh['id']:
                    for key in veh:
                        if key != 'id':
                            i.set(key,veh[key])    
    if addVeh:
        snap = tree.getroot()
        for veh in addVeh:
            #add new vehicle subelement
            ET.SubElement(snap, 'vehicle', attrib = veh['vehicle'])
            #add new route subelement corresponding to  vehicle's route
            ET.SubElement(snap, 'route', attrib = veh['route'])
            #place vehicle in appropriate lane
            for lane in snap.findall('lane'):
                #if lane matches lane id
                if lane.get('id') == veh['lane']:
                    # add vehicle to lane, but it needs to be in the right order
                    # first get the vid for each car in said lane 
                    lane_vehs = lane.find('vehicles').get('value')
                    lane_vehs = lane_vehs.split(' ')
                    lvpos = {}
                    for v in snap.findall('vehicle'):
                        if v.get('id') in lane_vehs:
                            lvpos[v.get('id')] = float(v.get('pos'))
                    lvpos[veh['vehicle']['id']] = float(veh['vehicle']['pos'])
                    vsort = sorted(lvpos, key=lvpos.get)
                    vsort = ' '.join(vsort)
                    lane.find('vehicles').set('value',vsort)
            n1 = int(tree.find('delay').get('begin'))
            n2 = int(tree.find('delay').get('number'))
            tree.find('delay').set('begin',str(n1+1))
            tree.find('delay').set('number',str(n2+1))
                    
    if remVeh:
        snap = tree.getroot()
        for veh in remVeh:
            veh_element = None
            for vehel in snap.findall('vehicle'):
                if vehel.get('id') == veh['id']:
                    veh_element = vehel
            if veh_element != None:
                for rouel in snap.findall('route'):
                    if rouel.get('id') == veh_element.get('route'):
                        # assumes rouel is only for vehicle being removed and not other vehicles
                        snap.remove(rouel)
                for lanel in snap.findall('lane'):
                    lane_vehs = lanel.find('vehicles').get('value')
                    lane_vehs = lane_vehs.split(' ')
                    if veh['id'] in lane_vehs:
                        lane_vehs.remove(veh['id'])
                        lanel.find('vehicles').set('value',' '.join(lane_vehs))
                snap.remove(veh_element)
            n1 = int(tree.find('delay').get('begin'))
            n2 = int(tree.find('delay').get('number'))
            tree.find('delay').set('begin',str(n1-1))
            tree.find('delay').set('number',str(n2-1))
        
    if newFile:
        writeFile = newFile
    else:
        writeFile = file
        
    with open(writeFile,'w+') as f:
        print('<%s version="%s" time="%s">' % (tree.getroot().tag,
                                              tree.getroot().get('version'),
                                              tree.getroot().get('time')),
                                              file=f)
        for el in tree.findall('route'):
            print(ET.tostring(el).decode('utf8'),file=f, end='')
        for el in tree.findall('delay'):
            print(ET.tostring(el).decode('utf8'),file=f, end='')
        for el in tree.findall('vType'):
            print(ET.tostring(el).decode('utf8'),file=f, end='')
        for el in tree.findall('vehicle'):
            print(ET.tostring(el).decode('utf8'),file=f, end='')
        for el in tree.findall('lane'):
            print(ET.tostring(el).decode('utf8'),file=f, end='')
        print('</%s>' % tree.getroot().tag, file=f)
        
                        
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

if __name__ == "__main__":
    add = [{'vehicle':{'depart': '10.00', 'id' : 'cat', 'pos' : '250', 
                      'posLat' : '0.00', 'route' : 'r_cat', 'speed' : '14.5',
                      'state' : '10000 0', #first num time of actual departure, second edge in route
                      'type' : 'DEFAULT_VEHTYPE'},
           'route':{'edges' : '1_2', 'id' : 'r_cat', 'state' : '1'},
           'lane':'1_2_0'}]
    
    forceUpdateBelief('simple_2d\\test.xml',changeVeh=[{'id':'4','pos':'10','depart':'8.00'}],
                      addVeh = add, remVeh = [{'id':'2'}], newFile = 'simple_2d\\out2.xml')