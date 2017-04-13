# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 14:51:48 2017

@author: jrobinson47
"""

import sys, subprocess, os
from utils.fusion_arch import Sensor

with open("local\\sumo.path", 'r') as f:
    sumo_path = f.read()
    sumo_tools = sumo_path + '\\tools'
    sumo_path += '\\bin'
    print(sumo_path)
    
if sumo_tools not in sys.path:
    sys.path.append(sumo_tools)

import traci

sim_globals = {'next_free_port': 8813}

def startTraciInstance(cfg,begin = None, state_opt = None):
    # create args for running sumo on next available port
    args = [sumo_path + '\\sumo-gui.exe',
            '-c', cfg,
            '--remote-port', str(sim_globals['next_free_port'])]
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
    t = traci.connect(sim_globals['next_free_port'])
    sim_globals['next_free_port'] += 1
    return p, t


    
    
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
    p_truth, truth = startTraciInstance(t_config)
    
    # load belief model (empty network)
    b_config = f_dir + '\\belief.sumocfg'
    genConfig(b_config,net)
    p_belief, belief = startTraciInstance(b_config)
    
    # propagate truth and belief
    # while cars remain in the truth model
    b_vehicles = []
    while truth.simulation.getMinExpectedNumber() > 0:
        truth.simulationStep()
        addSmartCars(truth,belief,b_vehicles,'smart')
        if fusion.sensors:
            senseDumbCars(truth,belief,b_vehicles,fusion)
        belief.simulationStep()
#        input('Press <ENTER> to continue')

    # optional: create secondary tracks for dumb cars passing intersections
    
    # belief queries smart cars from truth
    
    # belief receives sensor reports from truth via sensor model
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
                print(t.vehicle.getPosition(veh))
                print(t.vehicle.getSpeed(veh))
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
            m.append(mm)
    if m:
        print(m)
    
                
def compareStates(truth,belief):
    # compare state of belief to truth to acquire IQ metrics
    pass
