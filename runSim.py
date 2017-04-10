# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 14:51:48 2017

@author: jrobinson47
"""

import sys, subprocess

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
    args = [sumo_path + '\\sumo.exe',
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
    
def genConfig(cfg,net,route,add_args = None):
    args = [sumo_path + '\\sumo.exe',
            '--save-configuration', cfg,
            '-n', net,
            '-r', route]
    args = list(map(str,args))
    
    if add_args:
        args += add_args
        
    p = subprocess.Popen(args, stdout=subprocess.PIPE)
    p.wait()
    print(p.stdout.read().decode())
    
def runSim(net,route):
    # requires definition of simulation net and route as well as fusion framework
    # frequency of rerouting
    
    # load truth model
    # load belief model (empty network)
    
    # propagate truth and belief
    
    # optional: create secondary tracks for dumb cars passing intersections
    
    # belief queries smart cars from truth
    # belief receives sensor reports from truth via sensor model
    # fusion rules applied
    # belief state update
    pass

def compareStates(truth,belief):
    # compare state of belief to truth to acquire IQ metrics
    pass

runSim('oneway_data\\oneway.net.xml', 'oneway_data\\oneway.rou.xml')