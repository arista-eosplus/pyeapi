#!/usr/bin/env python

# import the client library
import pyeapi.client

# load the conf file and connect to the node
pyeapi.client.load_config('nodes.conf')
node = pyeapi.client.connect_to('veos01')

print 'Show running-config for veos01'
print '-'*30
print node.get_config('running-config')
print
print

print 'Show startup-config for veos01'
print '-'*30
print node.get_config('startup-config')
print
print

print 'Show config diffs'
print '-'*30
print node.get_config('running-config', 'diffs')
print
