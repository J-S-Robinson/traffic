# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 14:51:48 2017

@author: jrobinson47
"""

import sys, subprocess, os
from utils.fusion_arch import Sensor
from state_fix_utils import forceUpdateBelief

with open("local\\sumo.path", 'r') as f:
    sumo_path = f.read()
    sumo_tools = sumo_path + '\\tools'
    sumo_path += '\\bin'
    print(sumo_path)
    
if sumo_tools not in sys.path:
    sys.path.append(sumo_tools)

import traci

sim_globals = {'next_free_port': 8813, 'car_id' : 0}

def startTraciInstance(cfg,begin = None, state_opt = None, port=None):
    # create args for running sumo on next available port
    if port == None:
        port = sim_globals['next_free_port']
        sim_globals['next_free_port'] += 1
    
    args = [sumo_path + '\\sumo-gui.exe',
            '-c', cfg,
            '--remote-port', str(port)]
    if begin:
        args += ['--begin', str(begin)]
        
    if state_opt:
        if state_opt['mode'] in ('load','both'):
            args += ['--load-state', state_opt['load-file']]
        if state_opt['mode'] in ('save','both'):
            args += ['--save-state.period', state_opt['save-period']]
            args += ['--save-state.prefix', state_opt['save-prefix']]
            args += ['--save-state.suffix', '.xml']
    
    p = subprocess.Popen(args, stdout = subprocess.PIPE)
    
    t = traci.connect(port)
    return p, t, port


    
    
def genConfig(cfg,net,route = None,add_args = None):
    args = [sumo_path + '\\sumo.exe',
            '--save-configuration', cfg,
            '-n', net]
    if route:
        args += ['-r', route]
    
    if add_args:
        args += add_args
    args = list(map(str,args))    
    p = subprocess.Popen(args, stdout=subprocess.PIPE)
    p.wait()
    print(p.stdout.read().decode())
    
def runSim(net,route,reroutes,fusion=None):
    # requires definition of simulation net and route as well as fusion framework
    # frequency of rerouting
    
    # load truth model
    f_dir = os.path.split(net)[0]
    net = os.path.split(net)[1]
    route = os.path.split(route)[1]
    t_config = f_dir + '\\truth.sumocfg'
    
    if fusion:
        fusion.genDetectorFile(f_dir + '\\det.add.xml')
    genConfig(t_config,net,route = route, add_args = ['--additional-files','det.add.xml'])
    p_truth, truth, t_port = startTraciInstance(t_config)
    
    # load belief model (empty network)
    b_config = f_dir + '\\belief.sumocfg'
    genConfig(b_config,net)
    p_belief, belief, b_port = startTraciInstance(b_config)
    
    # propagate truth and belief
    # while cars remain in the truth model
    b_vehicles = []
    while truth.simulation.getMinExpectedNumber() > 0:
        truth.simulationStep()
        print("Propagating truth to t = " + str(truth.simulation.getCurrentTime()))
        if truth.simulation.getCurrentTime() == 51000:
            print('This step causing error')
    # belief queries smart cars from truth
        addSmartCars(truth,belief,b_vehicles,'smart')
    # belief receives sensor reports from truth via sensor model 
        if fusion.sensors:
            senseDumbCars(truth,belief,b_vehicles,fusion)
        belief.simulationStep()
        if int(truth.simulation.getCurrentTime()/1000) == 10:
#            belief.simulation.saveState('test.xml')
            add = [{'vehicle':{'depart': '10.00', 'id' : 'cat', 'pos' : '250', 
                                           'posLat' : '0.00', 'route' : 'r_cat', 'speed' : '14.5',
                                           'state' : '10000 0', #first num time of actual departure, second edge in route
                                           'type' : 'DEFAULT_VEHTYPE'},
                               'route':{'edges' : '1_2', 'id' : 'r_cat', 'state' : '1'},
                               'lane':'1_2_0'}]
            changedef = {'add':add, 'change':None, 'rem':None}
            p_belief, belief, b_port = restartWithNewStateFile(p_belief,belief,b_config,b_port,'simple_2d\\test1.xml',changedef,newFile='simple_2d\\test2.xml')
#        input('Press <ENTER> to continue')
    truth.close()
    belief.close()
    p_truth.kill()
    p_belief.kill()
    print('SIMULATION COMPLETE')
    # optional: create secondary tracks for dumb cars passing intersections

    # fusion rules applied
    # belief state update
    # if it's time for a reroute, do so.

def addSmartCars(t,b,b_list,vType):
    for veh in t.vehicle.getIDList():
        if t.vehicle.getTypeID(veh) == vType:
            if veh not in b_list:
                # add vehicle to network
                # need route id for vehicle to create it
                # get route of true vehicle
                new_rou = t.vehicle.getRoute(veh)
                if ('r_' + veh) not in b.route.getIDList():
                    b.route.add('r_' + veh, new_rou)
                b.vehicle.addFull(veh,'r_' + veh,
                                  depart = str(b.simulation.getCurrentTime()/1000),
                                  departLane = str(t.vehicle.getLaneIndex(veh)),
                                  departPos = str(t.vehicle.getPosition(veh)[1]),
                                  departSpeed = str(t.vehicle.getSpeed(veh)))
                b_list.append(veh)
                print('added %s' % veh)
                
def senseDumbCars(t,b,b_list,fus):
    m = []
    for sens in fus.sensors:
        mm = sens.genMeasurements(t, Sensor.measure_T_and_V)
        if mm:
            for mmm in mm:
                m.append(mmm)
    if m:
        for mm in m:           
            pos = [x.position for x in fus.sensors if x.id == mm['sensor']][0]
            # probs need to update position to next integral time
            # Get rid of hard coded route
            addVehicle(b,'s'+str(sim_globals['car_id']),['1_2'],mm['time'],
                       mm['lane'].split('_')[-1], 
                       pos, mm['speed'], vlist=b_list)
            sim_globals['car_id'] += 1
    

def addVehicle(traci_instance,vid,route,time,lane_ind,pos,speed,vlist=None):
    if ('r_' + vid) not in traci_instance.route.getIDList():
        traci_instance.route.add('r_' + vid, route)
    # maybe a better way?
    if time < traci_instance.simulation.getCurrentTime():
        pos = speed * (traci_instance.simulation.getCurrentTime()/1000 - time)
        time = traci_instance.simulation.getCurrentTime()/1000
    traci_instance.vehicle.addFull(vid, 'r_' + vid,
                                   depart = str(time),
                                   departLane = str(lane_ind),
                                   departPos = str(pos),
                                   departSpeed = str(speed))
    
    if vlist:
        vlist.append(vid)
    
def restartWithNewStateFile(p_sumo,traci,cfg,port,saveFile,changedef,newFile=None):
    # save current traci instance state
    traci.simulation.saveState(saveFile)
    # close sumo process
    traci.close()
    p_sumo.kill()
    # change state file
    # for now we'll assume it uses the forceUpdateBelief() function from state_fis_utils
    if newFile == None:
        newFile = saveFile
    if changedef['change']:
        change = changedef['change']
    else:
        change = None
    if changedef['add']:
        add = changedef['add']
    else:
        add = None
    if changedef['rem']:
        rem = changedef['rem']
    else:
        rem = None  
    forceUpdateBelief(saveFile,changeVeh = change,addVeh = add,remVeh = rem,
                      newFile = newFile)
    # load sumo with new or altered state file
    # connect to traci on same port
    state_opts = {'mode':'load', 'load-file':newFile} 
    pout, tout, portout = startTraciInstance(cfg,begin = None,
                                             state_opt = state_opts, port=port)
    return pout, tout, portout



def compareStates(truth,belief):
    # compare state of belief to truth to acquire IQ metrics
    pass

if __name__ == '__main__':
    p_truth, truth, t_port = startTraciInstance('simple_2d\\truth_db.sumocfg')
    truth.simulationStep()
    truth.simulationStep()
    print(truth.simulation.getCurrentTime())
    truth.simulationStep()
    print(truth.simulation.getCurrentTime())
    truth.simulationStep()
    print(truth.simulation.getCurrentTime())
    truth.simulationStep()
    print(truth.simulation.getCurrentTime())
    truth.simulationStep()
    print(truth.simulation.getCurrentTime())
    truth.simulationStep()
    print(truth.simulation.getCurrentTime())
    
