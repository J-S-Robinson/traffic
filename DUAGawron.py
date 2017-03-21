# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 15:04:31 2017

@author: Harvey
"""

#==============================================================================
# This code implements a variant of Gawron's method of Dynamic User Assignment
# for cases where only a subset of the vehicles can be routed. Additionally it
# is modified from SUMO's built in duaIterate.py to enable loading the traffic
# state from a state file, essentially starting the routing mid-simulation 
#==============================================================================
def runDUAIteratepartial():
    pass

def runSUMO(step):
    # First Generate Configuration for SUMO
    
    # Create Output File Definition
    outputFile = 'edgeData.out.xml'
    # Set period over which edge data is aggregated
    aggregation = 900;
    
    
    def writeSUMOConf(sumoBinary, step, options, additional_args, route_files,
                  state_file = None):
    detectorfile = "dua_dump_%03i.add.xml" % step
    comma = (',' if options.additional != "" else '')
    sumoCmd = [sumoBinary,
               '--save-configuration', "iteration_%03i.sumocfg" % step,
               '--net-file', options.net,
               '--route-files', route_files,
               '--additional-files', "%s%s%s" % (
                   detectorfile, comma, options.additional),
               '--no-step-log',
               '--random', options.absrand,
               '--begin', options.begin,
               '--route-steps', options.routeSteps,
               '--no-internal-links', options.internallink,
               '--eager-insert', options.eager_insert,
               '--verbose',
               '--no-warnings', options.noWarnings,
               ] + additional_args

    if hasattr(options, "noSummary") and not options.noSummary:
        sumoCmd += ['--summary-output', "summary_%03i.xml" % step]
    if hasattr(options, "noTripinfo") and not options.noTripinfo:
        sumoCmd += ['--tripinfo-output', "tripinfo_%03i.xml" % step]
        if options.ecomeasure:
            sumoCmd += ['--device.hbefa.probability', '1']
    if hasattr(options, "routefile"):
        if options.routefile == "routesonly":
            sumoCmd += ['--vehroute-output', "vehroute_%03i.xml" % step,
                        '--vehroute-output.route-length']
        elif options.routefile == "detailed":
            sumoCmd += ['--vehroute-output', "vehroute_%03i.xml" % step,
                        '--vehroute-output.route-length',
                        '--vehroute-output.exit-times']
    if hasattr(options, "lastroute") and options.lastroute:
        sumoCmd += ['--vehroute-output.last-route', options.lastroute]
    if hasattr(options, "timeInc") and options.timeInc:
        sumoCmd += ['--end', int(options.timeInc * (step + 1))]
    elif options.end:
        sumoCmd += ['--end', options.end]

    if hasattr(options, "incBase") and options.incBase > 0:
        sumoCmd += ['--scale', get_scale(options, step)]
    if options.mesosim:
        sumoCmd += ['--mesosim',
                    '--meso-recheck', options.mesorecheck]
        if options.mesomultiqueue:
            sumoCmd += ['--meso-multi-queue']
        if options.mesojunctioncontrol:
            sumoCmd += ['--meso-junction-control']
    
    # John -- make sure it starts with exact initial conditions
    if state_file != None:
         sumoCmd += ["--load-state",state_file]
    # make sure all arguments are strings
    sumoCmd = list(map(str, sumoCmd))
    # use sumoBinary to write a config file
    subprocess.call(sumoCmd, stdout=subprocess.PIPE)

    # write detectorfile
    with open(detectorfile, 'w') as fd:
        suffix = "_%03i_%s" % (step, options.aggregation)
        print("<a>", file=fd)
        if options.costmodifier != 'None':
            print('    <edgeData id="dump%s" freq="%s" file="%s" excludeEmpty="defaults" minSamples="1"/>' % (
                suffix, options.aggregation, get_dumpfilename(options, step, "dump")), file=fd)
        else:
            print('    <edgeData id="dump%s" freq="%s" file="%s" excludeEmpty="true" minSamples="1"/>' % (
                suffix, options.aggregation, get_dumpfilename(options, step, "dump")), file=fd)
        if options.ecomeasure:
            print('    <edgeData id="eco%s" type="hbefa" freq="%s" file="dump%s.xml" excludeEmpty="true" minSamples="1"/>' %
                  (suffix, options.aggregation, suffix), file=fd)
        print("</a>", file=fd)
    
    pass

def runDUAGawron(netfile,routefile,numIters=25):
    # for each time step, first run DUAITERATE and then SUMO
    for i in range(numIters):
        # DUAITERATE needs a route file and a network file as inputs
        # It also reads in the travel times from the previous iteration of 
        # SUMO to determine the edge weights of the network
        runDUAIterate()
        
        
        # SUMO also needs a route and network file as inputs it will output the
        # travel time on each edge, which will be used by the next iteration of
        # DUAITERATE
        runSUMO()