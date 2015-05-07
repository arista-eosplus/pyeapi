#!/usr/bin/env python
from __future__ import print_function
import pyeapi

pyeapi.load_config('nodes.conf')
node = pyeapi.connect_to('veos01')

print('Show running-config for veos01')
print(('-'*30))
print((node.get_config('running-config')))
print()
print()

print('Show startup-config for veos01')
print(('-'*30))
print((node.get_config('startup-config')))
print()
print()

print('Show config diffs')
print(('-'*30))
print((node.get_config('running-config', 'diffs')))
print()
