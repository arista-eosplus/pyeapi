#!/usr/bin/env python

import pyeapi.client

pyeapi.client.load_config('nodes.conf')
node = pyeapi.client.connect_to('veos01')

output = node.enable('show version')

print 'My System MAC address is', output[0]['systemMacAddress']
