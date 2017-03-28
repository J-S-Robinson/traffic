# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 15:04:31 2017

@author: Harvey
"""
import os
#==============================================================================
# This code implements a variant of Gawron's method of Dynamic User Assignment
# for cases where only a subset of the vehicles can be routed. Additionally it
# is modified from SUMO's built in duaIterate.py to enable loading the traffic
# state from a state file, essentially starting the routing mid-simulation 
#==============================================================================
import subprocess

def runDUAIteratepartial():
    pass

def runSUMO(sumoBinary, step, netFile, routeFile, outputFolder, outputFile,
            loadState = False, stateFile = '', begin=0):
    # First Generate Configuration for SUMO
    
    # Create Output File Definition
    
    # Create output configuration
    # Set period over which edge data is aggregated
    aggregation = 900
    
    addFile = outputFolder + '\\outputDef.add.xml'
    
    with open(addFile, 'w') as fd:
        print('<a>', file=fd)
        print('   <edgeData id="dump%s" freq="%s" file="%s" excludeEmpty="true" minSamples="1"/>'
              % (step, aggregation, outputFile), file=fd)
        print('</a>', file=fd)    
    
    sumoCmd = [sumoBinary, 
#               '--save-configuration', "iteration_%03i.sumocfg" % step,
               '--net-file', netFile,
               '--route-files',routeFile,
               '--additional-files', addFile,
               '--seed', '%s' % step,
               '--no-step-log',
               '--verbose',
               '--begin','%s' % begin]
    if loadState:
       sumoCmd += ['--load-state', stateFile]
    
    # make sure all arguments are strings
    sumoCmd = list(map(str, sumoCmd))
    # use sumoBinary to write a config file
#    subprocess.call(sumoCmd, stdout=subprocess.PIPE)
    p = subprocess.Popen(sumoCmd, stdout=subprocess.PIPE)
    p.wait()
    print(p.stdout.read().decode())
    
    
def runDUARouter(duarouterBinary, step, netFile, inputFile, outputFile, 
                 weightFile='', begin=0):
    routerCmd = [duarouterBinary,
                 '--net-file', netFile,
                 '--output-file', outputFile,
                 '--verbose', 'true',
                 '--gawron.a', '2.0',
                 '--gawron.beta', '0.05',
                 '--max-alternatives', '5',
                 '--weights.expand', 'true',
                 '--seed', '%s' % step,
                 '--begin', '%s' % begin]
    if step == 0:
        routerCmd += ['--route-files', inputFile]
    else:
        routerCmd += ['--alternative-files', inputFile,
                      '--weight-files', weightFile]
    routerCmd = list(map(str, routerCmd))
    
    p = subprocess.Popen(routerCmd, stdout=subprocess.PIPE)
    p.wait()
    print(p.stdout.read().decode())
    

def runDUAGawron(sumoBin, DUABin, netfile, routefile,
                 numIters=25,folder='DUA_data'):
    # output files are kept in a sub-folder for convenience
    os.makedirs(folder,exist_ok=True)
    # for each time step, first run DUAITERATE and then SUMO
    for i in range(numIters):
        # DUAITERATE needs a route file and a network file as inputs
        # It also reads in the travel times from the previous iteration of 
        # SUMO to determine the edge weights of the network
        if i == 0:
            runDUARouter(DUABin, i, netfile, routefile, folder+'\\tmp.rou.xml')
        else:
            runDUARouter(DUABin, i, netfile, routefile, folder+'\\tmp.rou.xml',
                         folder + '\\edgeData.xml')
        
        
        # SUMO also needs a route and network file as inputs it will output the
        # travel time on each edge, which will be used by the next iteration of
        # DUAITERATE
        runSUMO(sumoBin, i, netfile, 'DUA_data\\tmp.rou.xml', folder,
                'edgeData.xml')