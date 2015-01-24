#
# Copyright (c) 2014, Arista Networks, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#   Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
#   Neither the name of Arista Networks nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ARISTA NETWORKS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
import sys
import os
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))


from testlib import get_fixture, random_vlan, function
from testlib import EapiConfigUnitTest

import pyeapi.api.switchports

class TestApiSwitchports(EapiConfigUnitTest):

    INTERFACES = ['Ethernet1', 'Ethernet1/1', 'Port-Channel1']

    def __init__(self, *args, **kwargs):
        super(TestApiSwitchports, self).__init__(*args, **kwargs)
        self.instance = pyeapi.api.switchports.instance(None)
        self.config = open(get_fixture('running_config.text')).read()

    def test_get(self):
        result = self.instance.get('Ethernet1')
        values = dict(name='Ethernet1', mode='access', access_vlan='1',
                      trunk_native_vlan='1', trunk_allowed_vlans='1-4094')
        self.assertEqual(result, values)

    def test_getall(self):
        result = self.instance.getall()
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 7)

    def test_instance_functions(self):
        for intf in self.INTERFACES:
            for name in ['create', 'delete', 'default']:
                if name == 'create':
                    cmds = ['interface %s' % intf, 'no ip address',
                            'switchport']

                elif name == 'delete':
                    cmds = ['interface %s' % intf, 'no switchport']

                elif name == 'default':
                    cmds = ['interface %s' % intf, 'no ip address',
                            'default switchport']

                func = function(name, intf)
                self.eapi_positive_config_test(func, cmds)

    def test_set_mode(self):
        for intf in self.INTERFACES:
            for mode in ['access', 'trunk']:
                cmds = ['interface %s' % intf, 'switchport mode %s' % mode]
                func = function('set_mode', intf, mode)
                self.eapi_positive_config_test(func, cmds)

    def test_set_mode_with_no_value(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf, 'no switchport mode']
            func = function('set_mode', intf)
            self.eapi_positive_config_test(func, cmds)

    def test_set_mode_with_default(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf, 'default switchport mode']
            func = function('set_mode', intf, default=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_access_vlan(self):
        for intf in self.INTERFACES:
            vid = random_vlan()
            cmds = ['interface %s' % intf, 'switchport access vlan %s' % vid]
            func = function('set_access_vlan', intf, vid)
            self.eapi_positive_config_test(func, cmds)

    def test_set_access_vlan_with_no_value(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf, 'no switchport access vlan']
            func = function('set_access_vlan', intf)
            self.eapi_positive_config_test(func, cmds)

    def test_set_access_vlan_with_default(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf, 'default switchport access vlan']
            func = function('set_access_vlan', intf, default=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_trunk_native_vlan(self):
        for intf in self.INTERFACES:
            vid = random_vlan()
            cmds = ['interface %s' % intf,
                    'switchport trunk native vlan %s' % vid]
            func = function('set_trunk_native_vlan', intf, vid)
            self.eapi_positive_config_test(func, cmds)

    def test_set_trunk_native_vlan_with_no_value(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf, 'no switchport trunk native vlan']
            func = function('set_trunk_native_vlan', intf)
            self.eapi_positive_config_test(func, cmds)

    def test_set_trunk_native_vlan_with_default(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf,
                    'default switchport trunk native vlan']
            func = function('set_trunk_native_vlan', intf, default=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_trunk_allowed_vlans(self):
        for intf in self.INTERFACES:
            vid = '1,2,3-5,6,7'
            cmds = ['interface %s' % intf,
                    'switchport trunk allowed vlan %s' % vid]
            func = function('set_trunk_allowed_vlans', intf, vid)
            self.eapi_positive_config_test(func, cmds)

    def test_set_trunk_allowed_vlans_with_no_value(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf,
                    'no switchport trunk allowed vlan']
            func = function('set_trunk_allowed_vlans', intf)
            self.eapi_positive_config_test(func, cmds)

    def test_set_allowed_vlans_with_default(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf,
                    'default switchport trunk allowed vlan']
            func = function('set_trunk_allowed_vlans', intf, default=True)
            self.eapi_positive_config_test(func, cmds)

if __name__ == '__main__':
    unittest.main()


