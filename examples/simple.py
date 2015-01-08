#!/usr/bin/env python

import pyeapi.client

connection = pyeapi.client.connect(host='192.168.1.16', use_ssl=False)
output = connection.execute(['enable', 'show version'])

print 'My system MAC address is', output['result'][1]['systemMacAddress']


