# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 23:49:57 2017

@author: Harvey
"""
import xml.etree.ElementTree as ET
from subprocess import Popen,PIPE

class Node: 
    
    def __init__(self,ID,x,y,isTL=False):
        self.ID = ID
        self.x = x
        self.y = y
        self.isTL = isTL

class Edge:
    
    def __init__(self,start,end,numLanes=1,speed=15):
        #start and end are Nodes
        self.startNode = start
        self.endNode = end
        self.numLanes = numLanes
        self.speed = speed
        self.ID = '_'.join((self.startNode.ID,self.endNode.ID))
        
class Network:
    
    def __init__(self,nodes,edges):
        self.nodes = nodes
        self.edges = edges
        
    def _genEdgeFile(self,out):
        edgeRoot = ET.Element('edges')
        for edge in self.edges:
            new_edge = ET.Element('edge',
                                  attrib = {'from':edge.startNode.ID,
                                            'to':edge.endNode.ID,
                                            'numLanes':'%i' % edge.numLanes,
                                            'speed':'%i' % edge.speed,
                                            'id':edge.ID})
            edgeRoot.append(new_edge)
        edgeTree = ET.ElementTree()
        edgeTree._setroot(edgeRoot)
        edgeTree.write(out)
        
    def _genNodeFile(self,out):
        nodeRoot = ET.Element('nodes')
        for node in self.nodes:
            new_node = ET.Element('node',
                                  attrib = {'x':'%i' % node.x,
                                            'y':'%i' % node.y,
                                            'id':node.ID})
            if node.isTL:
                new_node.set('type','traffic_light')
            nodeRoot.append(new_node)
        nodeTree = ET.ElementTree()
        nodeTree._setroot(nodeRoot)
        nodeTree.write(out)
        
    def _genConNoUturn(self,out):
        conRoot = ET.Element('connections')
        for edge1 in self.edges:
            for edge2 in self.edges:
                if (edge1.endNode == edge2.startNode and
                        edge1.startNode != edge2.endNode):
                    new_con=ET.Element('connection',
                                       attrib = {'from':edge1.ID,
                                                 'to':edge2.ID})
                    conRoot.append(new_con)
        conTree = ET.ElementTree()
        conTree._setroot(conRoot)
        conTree.write(out)
        
    def writeNet(self,sumo_path,nameroot):
        self._genNodeFile('%s.nod.xml' % nameroot)
        self._genEdgeFile('%s.edg.xml' % nameroot)
        self._genConNoUturn('%s.con.xml' % nameroot)
        p = Popen(['%s\\netconvert.exe' % sumo_path,
              '-n','%s.nod.xml' % nameroot,
              '-e','%s.edg.xml' % nameroot,
              '-x', '%s.con.xml' % nameroot,
              '-o', '%s.net.xml' % nameroot],stdout=PIPE)
        p.wait()
        print(p.stdout.read().decode())


    
    