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

from testlib import get_fixture, random_string, function
from testlib import EapiConfigUnitTest

import pyeapi.api.interfaces

INTERFACES = ['Ethernet1', 'Ethernet1/1', 'Vlan1234', 'Management1',
              'Port-Channel1', 'Vxlan1']

class TestFunctions(unittest.TestCase):

    def test_isvalidinterface_returns_true(self):
        func = pyeapi.api.interfaces.isvalidinterface
        for intf in INTERFACES:
            self.assertTrue(func(intf))

    def test_isvalidinterface_returns_false(self):
        func = pyeapi.api.interfaces.isvalidinterface
        for intf in ['Et1', 'Ma1', 'Po1', 'Vl1', random_string()]:
            self.assertFalse(func(intf))

    def test_instance(self):
        result = pyeapi.api.interfaces.instance(None)
        self.assertIsInstance(result, pyeapi.api.interfaces.Interfaces)


class TestApiInterfaces(EapiConfigUnitTest):

    def __init__(self, *args, **kwargs):
        super(TestApiInterfaces, self).__init__(*args, **kwargs)
        self.instance = pyeapi.api.interfaces.Interfaces(None)
        self.config = open(get_fixture('running_config.text')).read()

    def test_get_interface_generic(self):
        for intf in ['Management1', 'Loopback0']:
            result = self.instance.get(intf)
            self.assertEqual(result['type'], 'generic')

    def test_get_interface_ethernet(self):
        result = self.instance.get('Ethernet1')
        self.assertEqual(result['type'], 'ethernet')

    def test_proxy_method_success(self):
        result = self.instance.set_sflow('Ethernet1', True)
        self.assertTrue(result)

    def test_proxy_method_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.instance.set_sflow('Management1', True)



class TestApiBaseInterface(EapiConfigUnitTest):

    def __init__(self, *args, **kwargs):
        super(TestApiBaseInterface, self).__init__(*args, **kwargs)
        self.instance = pyeapi.api.interfaces.BaseInterface(None)
        self.config = open(get_fixture('running_config.text')).read()

    def test_get(self):
        result = self.instance.get('Loopback0')
        values = dict(name='Loopback0', type='generic',
                      shutdown=False, description='')
        self.assertEqual(result, values)

    def test_set_description_with_value(self):
        for intf in INTERFACES:
            value = random_string()
            cmds = ['interface %s' % intf, 'description %s' % value]
            func = function('set_description', intf, value)
            self.eapi_positive_config_test(func, cmds)

    def test_set_description_with_no_value(self):
        for intf in INTERFACES:
            cmds = ['interface %s' % intf, 'no description']
            func = function('set_description', intf)
            self.eapi_positive_config_test(func, cmds)

    def test_set_description_with_default(self):
        for intf in INTERFACES:
            cmds = ['interface %s' % intf, 'default description']
            func = function('set_description', intf, default=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_shutdown_with_value(self):
        for intf in INTERFACES:
            for value in [True, False]:
                cmds = ['interface %s' % intf]
                if value:
                    cmds.append('shutdown')
                else:
                    cmds.append('no shutdown')
                func = function('set_shutdown', intf, value)
                self.eapi_positive_config_test(func, cmds)

    def test_set_shutdown_with_no_value(self):
        for intf in INTERFACES:
            cmds = ['interface %s' % intf, 'no shutdown']
            func = function('set_shutdown', intf)
            self.eapi_positive_config_test(func, cmds)

    def test_set_shutdown_with_default(self):
        for intf in INTERFACES:
            cmds = ['interface %s' % intf, 'default shutdown']
            func = function('set_shutdown', intf, default=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_shutdown_invalid_value_raises_value_error(self):
        for intf in INTERFACES:
            func = function('set_shutdown', intf, random_string())
            self.eapi_exception_config_test(func, ValueError)



class TestApiEthernetInterface(EapiConfigUnitTest):

    INTERFACES = ['Ethernet1', 'Ethernet1/1']

    def __init__(self, *args, **kwargs):
        super(TestApiEthernetInterface, self).__init__(*args, **kwargs)
        self.instance = pyeapi.api.interfaces.EthernetInterface(None)
        self.config = open(get_fixture('running_config.text')).read()

    def test_get(self):
        result = self.instance.get('Ethernet1')
        values = dict(name='Ethernet1', type='ethernet',
                      description='', shutdown=False,
                      sflow=True, flowcontrol_send='off',
                      flowcontrol_receive='off')
        self.assertEqual(values, result)

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

    def test_set_flowcontrol_with_value(self):
        for intf in self.INTERFACES:
            for direction in ['send', 'receive']:
                for value in ['on', 'off']:
                    cmds = ['interface %s' % intf,
                            'flowcontrol %s %s' % (direction, value)]
                    func = function('set_flowcontrol', intf, direction, value)
                    self.eapi_positive_config_test(func, cmds)

    def test_set_flowcontrol_with_invalid_direction_raises_value_error(self):
        for intf in self.INTERFACES:
            func = function('set_flowcontrol', intf, 'invalid', None)
            self.eapi_exception_config_test(func, ValueError)

    def test_set_flowcontrol_with_invalid_value_raises_value_error(self):
        for intf in self.INTERFACES:
            for direction in ['send', 'receive']:
                func = function('set_flowcontrol', intf, direction, 'invalid')
                self.eapi_exception_config_test(func, ValueError)

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


    def test_set_sflow_with_value(self):
        for intf in self.INTERFACES:
            for value in [True, False]:
                cmds = ['interface %s' % intf]
                if value:
                    cmds.append('sflow enable')
                else:
                    cmds.append('no sflow enable')
                func = function('set_sflow', intf, value)
                self.eapi_positive_config_test(func, cmds)

    def test_set_sflow_with_no_value(self):
        for intf in INTERFACES:
            cmds = ['interface %s' % intf, 'no sflow enable']
            func = function('set_sflow', intf)
            self.eapi_positive_config_test(func, cmds)

    def test_set_sflow_with_default(self):
        for intf in INTERFACES:
            cmds = ['interface %s' % intf, 'default sflow']
            func = function('set_sflow', intf, default=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_shutdown_invalid_value_raises_value_error(self):
        for intf in INTERFACES:
            func = function('set_sflow', intf, random_string())
            self.eapi_exception_config_test(func, ValueError)

if __name__ == '__main__':
    unittest.main()


