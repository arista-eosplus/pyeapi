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
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))

from testlib import get_fixture, random_string, function
from testlib import EapiConfigUnitTest

import pyeapi.resources.interfaces

class TestModuleInterfaces(EapiConfigUnitTest):

    INTERFACES = ['Ethernet1', 'Ethernet1/1', 'Vlan1234', 'Management1',
                  'Port-Channel1', 'Vxlan1']

    def __init__(self, *args, **kwargs):
        super(TestModuleInterfaces, self).__init__(*args, **kwargs)
        self.instance = pyeapi.resources.interfaces.instance(None)
        self.running_config = open(get_fixture('running_config.text')).read()

    def test_get(self):
        result = self.instance.get('Ethernet1')
        values = dict(name='Ethernet1', description='', shutdown=False,
                      sflow=True, flowcontrol_send='off',
                      flowcontrol_receive='off')
        self.assertEqual(values, result)

    def test_getall(self):
        result = self.instance.getall()
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 10)

    def test_instance_functions(self):
        for intf in self.INTERFACES:
            for name in ['create', 'delete', 'default']:
                if name == 'create':
                    if intf[0:2] not in ['Et', 'Ma']:
                        cmds = 'interface %s' % intf
                        func = function(name, intf)
                        self.eapi_positive_config_test(func, cmds)
                elif name == 'delete':
                    if intf[0:2] not in ['Et', 'Ma']:
                        cmds = 'no interface %s' % intf
                        func = function(name, intf)
                        self.eapi_positive_config_test(func, cmds)
                elif name == 'default':
                    cmds = 'default interface %s' % intf
                    func = function(name, intf)
                    self.eapi_positive_config_test(func, cmds)

    def test_set_description_with_value(self):
        for intf in self.INTERFACES:
            value = random_string()
            cmds = ['interface %s' % intf, 'description %s' % value]
            func = function('set_description', intf, value)
            self.eapi_positive_config_test(func, cmds)

    def test_set_description_with_no_value(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf, 'no description']
            func = function('set_description', intf)
            self.eapi_positive_config_test(func, cmds)

    def test_set_description_with_default(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf, 'default description']
            func = function('set_description', intf, default=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_shutdown_with_value(self):
        for intf in self.INTERFACES:
            for value in [True, False]:
                value = random_string()
                cmds = ['interface %s' % intf]
                if value:
                    cmds.append('shutdown')
                else:
                    cmds.append('no shutdown')
                func = function('set_shutdown', intf, value)
                self.eapi_positive_config_test(func, cmds)

    def test_set_shutdown_with_no_value(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf, 'no shutdown']
            func = function('set_shutdown', intf)
            self.eapi_positive_config_test(func, cmds)

    def test_set_shutdown_with_default(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf, 'default shutdown']
            func = function('set_shutdown', intf, default=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_flowcontrol_with_values(self):
        for intf in self.INTERFACES:
            for direction in ['send', 'receive']:
                for value in ['on' 'off', 'desired']:
                    cmds = ['interface %s' % intf,
                            'flowcontrol %s %s' % (direction, value)]
                    func = function('set_flowcontrol', intf, direction, value)
                    self.eapi_positive_config_test(func, cmds)

    def test_set_flowcontrol_with_invalid_direction(self):
        for intf in self.INTERFACES:
            func = function('set_flowcontrol', intf, 'invalid', None)
            self.eapi_negative_config_test(func)

    def test_set_flowcontrol_with_invalid_value(self):
        for intf in self.INTERFACES:
            for direction in ['send', 'receive']:
                func = function('set_flowcontrol', intf, direction, 'invalid')
                self.eapi_negative_config_test(func)

    def test_set_flowcontrol_with_no_value(self):
        for intf in self.INTERFACES:
            for direction in ['send', 'receive']:
                cmds = ['interface %s' % intf, 'no flowcontrol %s' % direction]
                func = function('set_flowcontrol', intf, direction)
                self.eapi_positive_config_test(func, cmds)

    def test_set_flowcontrol_with_default(self):
        for intf in self.INTERFACES:
            for direction in ['send', 'receive']:
                cmds = ['interface %s' % intf,
                        'default flowcontrol %s' % direction]
                func = function('set_flowcontrol', intf, direction,
                                default=True)
                self.eapi_positive_config_test(func, cmds)


if __name__ == '__main__':
    unittest.main()


