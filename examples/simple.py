#!/usr/bin/env python

import pyeapi

connection = pyeapi.connect(host='192.168.1.16')
output = connection.execute(['enable', 'show version'])

print 'My system MAC address is', output['result'][1]['systemMacAddress']


