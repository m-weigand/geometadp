# -*- coding: utf-8 -*-
"""
Created on Wed May  5 12:08:57 2021

@author: Benjamin
"""
import expipe
import os

project = expipe.require_project("test")


action = project.require_action("something")
from datetime import datetime
action.tags = ['place cell', 'familiar environment']
action.datetime = datetime.now()
action.location = 'here'
action.type = 'Recording'
action.subjects = ['rat1']
action.users = ['Peter', 'Mary']

tracking = action.require_module("tracking", template="tracking")

import quantities as pq
tracking_contents = {'box_shape': {'value': 'square'}}
tracking_module = action.require_module(name="tracking",
                                        contents=tracking_contents)
elphys_contents = {'depth': 2 * pq.um, }
elphys_module = action.require_module(name="electrophysiology",
                                      contents=elphys_contents)

for name, val in action.modules.items():
     if name == 'electrophysiology':
         print(val['depth'])

tracking = action.require_module(name="tracking")
print(tracking.to_dict())


daq_contents = {
    "channel_count": {"definition": "The number of input channels of the DAQ-device.",
                      "value": "64"}}
expipe.require_template(template='hardware_daq',
                        contents=daq_contents)

daq = action.require_module(template='hardware_daq')

daq_dict = daq.to_dict()
print(daq_dict.keys())




from datetime import datetime
messages = [{'message': 'hello', 'user': 'Peter', 'datetime': datetime.now()}]
action.messages = messages


