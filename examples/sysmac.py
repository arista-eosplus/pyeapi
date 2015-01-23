#!/usr/bin/env python

import pyeapi

pyeapi.load_config('nodes.conf')
node = pyeapi.connect_to('veos01')

output = node.enable('show version')

print 'My System MAC address is', output[0]['result']['systemMacAddress']
