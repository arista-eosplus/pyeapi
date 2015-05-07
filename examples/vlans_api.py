#!/usr/bin/env python
from __future__ import print_function
# import the client library
import pyeapi

# load the conf file and connect to the node
pyeapi.load_config('nodes.conf')
node = pyeapi.connect_to('veos01')

# get the vlan api and enable autorefresh
vlans = node.api('vlans')
vlans.autorefresh = True

if vlans.get(123):
    print('Vlan 123 already exists, deleting it')
    vlans.delete(1234)

print('\nCreating Vlan 123')
vlans.create(123)

print('Setting Vlan 123 name to "test_vlan"')
vlans.set_name(123, 'test_vlan')

print('\nDisplaying all vlans on the node')
print(('-'*30))
for vlan in list(vlans.values()):
    print(("   Vlan Id: {vlan_id}, Name: {name}".format(**vlan)))

if vlans.get(123):
    print('\nDeleting Vlan 123')
    vlans.delete(123)

print()


