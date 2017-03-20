# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 14:15:09 2017

@author: jrobinson47
"""

import duaIterate3
import xml.etree.ElementTree as ET
import state_fix_utils as SFU
import route_online_test as ROT

dumbCars = ['1', '3', '7', '10']

num_iters = 15
duaIterate3.runDuaIterate('data\\cat.net.xml','data\\snap_30.rou.xml',num_iters,
                          statefile='data\\cat_state_30.00.xml',
                          start_time='30',dumb_cars=dumbCars)

rou_out = 'data\\snap_30_%03i.rou.xml' % (num_iters - 1)

statefile = ('data\\cat_state_30.00.xml')

newstatefile = ('data\\cat_state_30.00u.xml')

SFU.update_state_routes(statefile,rou_out,newstatefile)
