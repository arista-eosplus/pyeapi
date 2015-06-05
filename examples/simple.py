#!/usr/bin/env python
from __future__ import print_function
import pyeapi

connection = pyeapi.connect(host='192.168.1.16')
output = connection.execute(['enable', 'show version'])

print(('My system MAC address is', output['result'][1]['systemMacAddress']))


