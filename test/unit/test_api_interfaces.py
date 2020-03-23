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

from testlib import get_fixture, random_string, function, random_int
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

    def test_get_invalid_interface(self):
        result = self.instance.get('Foo1')
        self.assertEqual(result, None)

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
                      shutdown=False, description=None)
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
            func = function('set_description', intf, disable=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_description_with_default(self):
        for intf in INTERFACES:
            cmds = ['interface %s' % intf, 'default description']
            func = function('set_description', intf, default=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_shutdown(self):
        for intf in INTERFACES:
            cmds = ['interface %s' % intf, 'shutdown']
            func = function('set_shutdown', intf, default=False, disable=False)
            self.eapi_positive_config_test(func, cmds)

    def test_set_shutdown_with_disable(self):
        for intf in INTERFACES:
            cmds = ['interface %s' % intf, 'no shutdown']
            func = function('set_shutdown', intf)
            self.eapi_positive_config_test(func, cmds)

    def test_set_shutdown_with_default(self):
        for intf in INTERFACES:
            cmds = ['interface %s' % intf, 'default shutdown']
            func = function('set_shutdown', intf, default=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_encapsulation_non_subintf(self):
        cmds = ['interface Ethernet1', 'encapsulation dot1q vlan 4']
        func = function('set_encapsulation', 'Ethernet1', 4)
        self.eapi_exception_config_test(func, NotImplementedError,
                                        cmds)

    def test_set_encapsulation_non_supported_intf(self):
        cmds = ['interface Vlan1234', 'encapsulation dot1q vlan 4']
        func = function('set_encapsulation', 'Vlan1234', 4)
        self.eapi_exception_config_test(func, NotImplementedError,
                                        cmds)

    def test_set_encapsulation_ethernet_subintf(self):
        cmds = ['interface Ethernet1.1', 'encapsulation dot1q vlan 4']
        func = function('set_encapsulation', 'Ethernet1.1', 4)
        self.eapi_positive_config_test(func, cmds)

    def test_set_encapsulation_portchannel_subintf_disable(self):
        cmds = ['interface Port-Channel1.1', 'no encapsulation dot1q vlan']
        func = function('set_encapsulation', 'Port-Channel1.1', 4,
                        disable=True)
        self.eapi_positive_config_test(func, cmds)

    def test_set_encapsulation_ethernet_subintf_default(self):
        cmds = ['interface Ethernet1.1', 'default encapsulation dot1q vlan']
        func = function('set_encapsulation', 'Ethernet1.1', 4,
                        default=True)
        self.eapi_positive_config_test(func, cmds)


class TestApiEthernetInterface(EapiConfigUnitTest):

    INTERFACES = ['Ethernet1', 'Ethernet1/1']

    def __init__(self, *args, **kwargs):
        super(TestApiEthernetInterface, self).__init__(*args, **kwargs)
        self.instance = pyeapi.api.interfaces.EthernetInterface(None)
        self.config = open(get_fixture('running_config.text')).read()

    def test_get(self):
        result = self.instance.get('Ethernet1')
        values = dict(name='Ethernet1', type='ethernet',
                      description=None, shutdown=False,
                      sflow=True, flowcontrol_send='off',
                      flowcontrol_receive='off')
        self.assertEqual(values, result)

    def test_instance_functions(self):
        for intf in self.INTERFACES:
            for name in ['create', 'delete', 'default']:
                if name == 'create':
                    # Test create for subinterfaces
                    subintf = intf + '.1'
                    cmds = ['interface %s' % subintf]
                    func = function(name, subintf)
                    self.eapi_positive_config_test(func, cmds)
                elif name == 'delete':
                    # Test delete for subinterfaces
                    subintf = intf + '.1'
                    cmds = ['no interface %s' % subintf]
                    func = function(name, subintf)
                    self.eapi_positive_config_test(func, cmds)
                elif name == 'default':
                    cmds = 'default interface %s' % intf
                    func = function(name, intf)
                    self.eapi_positive_config_test(func, cmds)

    def test_instance_functions_exceptions(self):
        intf = 'Ethernet1'
        for name in ['create', 'delete']:
            if name == 'create':
                cmds = 'interface %s' % intf
                func = function(name, intf)
                self.eapi_exception_config_test(func, NotImplementedError,
                                                cmds)
            elif name == 'delete':
                cmds = 'no interface %s' % intf
                func = function(name, intf)
                self.eapi_exception_config_test(func, NotImplementedError,
                                                cmds)

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

    def test_set_flowcontrol_with_disable(self):
        for intf in self.INTERFACES:
            for direction in ['send', 'receive']:
                cmds = ['interface %s' % intf, 'no flowcontrol %s' % direction]
                func = function('set_flowcontrol', intf, direction,
                                disable=True)
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
            cmds = ['interface %s' % intf, 'default sflow enable']
            func = function('set_sflow', intf, default=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_sflow_invalid_value_raises_value_error(self):
        for intf in INTERFACES:
            func = function('set_sflow', intf, random_string())
            self.eapi_exception_config_test(func, ValueError)

    def test_set_vrf(self):
        for intf in INTERFACES:
            vrf = 'testvrf'
            cmds = ['interface %s' % intf, 'vrf forwarding %s' % vrf]
            func = function('set_vrf', intf, vrf)
            self.eapi_positive_config_test(func, cmds)


class TestApiPortchannelInterface(EapiConfigUnitTest):

    def __init__(self, *args, **kwargs):
        super(TestApiPortchannelInterface, self).__init__(*args, **kwargs)
        self.instance = pyeapi.api.interfaces.PortchannelInterface(None)
        self.config = open(get_fixture('running_config.portchannel')).read()

    def setUp(self):
        super(TestApiPortchannelInterface, self).setUp()
        response = open(get_fixture('show_portchannel.json'))
        self.node.enable.return_value = json.load(response)
        response.close()

    def test_get(self):
        result = self.instance.get('Port-Channel1')
        values = dict(name='Port-Channel1', type='portchannel',
                      description=None, shutdown=False,
                      lacp_mode='on', minimum_links=0,
                      lacp_fallback='disabled', lacp_timeout=90,
                      members=['Ethernet5', 'Ethernet6'])

        self.assertEqual(values, result)

    def test_set_minimum_links_with_value(self):
        minlinks = random_int(1, 16)
        cmds = ['interface Port-Channel1',
                'port-channel min-links %s' % minlinks]
        func = function('set_minimum_links', 'Port-Channel1', minlinks)
        self.eapi_positive_config_test(func, cmds)

    def test_set_minimum_links_with_no_value(self):
        cmds = ['interface Port-Channel1', 'no port-channel min-links']
        func = function('set_minimum_links', 'Port-Channel1')
        self.eapi_positive_config_test(func, cmds)

    def test_set_minimum_links_with_default(self):
        cmds = ['interface Port-Channel1', 'default port-channel min-links']
        func = function('set_minimum_links', 'Port-Channel1', default=True)
        self.eapi_positive_config_test(func, cmds)

    def test_set_minimum_links_with_disable(self):
        cmds = ['interface Port-Channel1', 'no port-channel min-links']
        func = function('set_minimum_links', 'Port-Channel1', disable=True)
        self.eapi_positive_config_test(func, cmds)

    def test_set_lacp_timeout_with_value(self):
        timeout = random_int(1, 16)
        cmds = ['interface Port-Channel1', 'port-channel lacp fallback timeout %s' % timeout]
        func = function('set_lacp_timeout', 'Port-Channel1', timeout)
        self.eapi_positive_config_test(func, cmds)

    def test_set_lacp_fallback_with_individual(self):
        cmds = ['interface Port-Channel1', 'port-channel lacp fallback individual']
        func = function('set_lacp_fallback', 'Port-Channel1', 'individual')
        self.eapi_positive_config_test(func, cmds)

    def test_set_lacp_fallback_with_static(self):
        cmds = ['interface Port-Channel1', 'port-channel lacp fallback static']
        func = function('set_lacp_fallback', 'Port-Channel1', 'static')
        self.eapi_positive_config_test(func, cmds)

    def test_set_lacp_fallback_with_disabled(self):
        cmds = ['interface Port-Channel1', 'no port-channel lacp fallback']
        func = function('set_lacp_fallback', 'Port-Channel1', 'disabled')
        self.eapi_positive_config_test(func, cmds)

    def test_set_lacp_fallback_invalid_mode(self):
        func = function('set_lacp_fallback', 'Port-Channel1', random_string())
        self.eapi_negative_config_test(func)

    def test_get_lacp_mode(self):
        result = self.instance.get_lacp_mode('Port-Channel1')
        self.assertEqual(result, 'on')

    def test_get_members(self):
        result = self.instance.get_members('Port-Channel1')
        self.assertEqual(result, ['Ethernet5', 'Ethernet6'])

    def test_set_members(self):
        cmds = ['interface Ethernet6', 'no channel-group 1',
                'interface Ethernet7', 'channel-group 1 mode on']
        func = function('set_members', 'Port-Channel1',
                        ['Ethernet5', 'Ethernet7'])
        self.eapi_positive_config_test(func, cmds)

    def test_set_members_same_mode(self):
        cmds = ['interface Ethernet6', 'no channel-group 1',
                'interface Ethernet7', 'channel-group 1 mode on']
        func = function('set_members', 'Port-Channel1',
                        ['Ethernet5', 'Ethernet7'])
        self.eapi_positive_config_test(func, cmds)

    def test_set_members_update_mode(self):
        cmds = ['interface Ethernet6', 'no channel-group 1',
                'interface Ethernet7', 'channel-group 1 mode active']
        func = function('set_members', 'Port-Channel1',
                        ['Ethernet5', 'Ethernet7'], mode='active')
        self.eapi_positive_config_test(func, cmds)

    def test_set_members_mode_none(self):
        cmds = ['interface Ethernet6', 'no channel-group 1',
                'interface Ethernet7', 'channel-group 1 mode on']
        func = function('set_members', 'Port-Channel1',
                        ['Ethernet5', 'Ethernet7'], mode=None)
        self.eapi_positive_config_test(func, cmds)

    def test_set_members_no_changes(self):
        func = function('set_members', 'Port-Channel1',
                        ['Ethernet5', 'Ethernet6'])
        self.eapi_positive_config_test(func)

    def test_set_lacp_mode(self):
        cmds = ['interface Ethernet5', 'no channel-group 1',
                'interface Ethernet6', 'no channel-group 1',
                'interface Ethernet5', 'channel-group 1 mode active',
                'interface Ethernet6', 'channel-group 1 mode active']
        func = function('set_lacp_mode', 'Port-Channel1', 'active')
        self.eapi_positive_config_test(func, cmds)

    def test_set_lacp_mode_invalid_mode(self):
        func = function('set_lacp_mode', 'Port-Channel1', random_string())
        self.eapi_negative_config_test(func)


class TestApiVxlanInterface(EapiConfigUnitTest):

    def __init__(self, *args, **kwargs):
        super(TestApiVxlanInterface, self).__init__(*args, **kwargs)
        self.instance = pyeapi.api.interfaces.VxlanInterface(None)
        self.config = open(get_fixture('running_config.vxlan')).read()

    def test_get(self):
        keys = ['name', 'type', 'description', 'shutdown', 'source_interface',
                'multicast_group', 'udp_port', 'vlans', 'flood_list',
                'multicast_decap']
        result = self.instance.get('Vxlan1')
        self.assertEqual(sorted(keys), sorted(result.keys()))

    def test_set_source_interface_with_value(self):
        cmds = ['interface Vxlan1', 'vxlan source-interface Loopback0']
        func = function('set_source_interface', 'Vxlan1', 'Loopback0')
        self.eapi_positive_config_test(func, cmds)

    def test_set_source_interface_with_no_value(self):
        cmds = ['interface Vxlan1', 'no vxlan source-interface']
        func = function('set_source_interface', 'Vxlan1', disable=True)
        self.eapi_positive_config_test(func, cmds)

    def test_set_source_interface_with_default(self):
        cmds = ['interface Vxlan1', 'default vxlan source-interface']
        func = function('set_source_interface', 'Vxlan1', default=True)
        self.eapi_positive_config_test(func, cmds)

    def test_set_multicast_group_with_value(self):
        cmds = ['interface Vxlan1', 'vxlan multicast-group 239.10.10.10']
        func = function('set_multicast_group', 'Vxlan1', '239.10.10.10')
        self.eapi_positive_config_test(func, cmds)

    def test_set_multicast_group_with_no_value(self):
        cmds = ['interface Vxlan1', 'no vxlan multicast-group']
        func = function('set_multicast_group', 'Vxlan1', disable=True)
        self.eapi_positive_config_test(func, cmds)

    def test_set_multicast_group_with_default(self):
        cmds = ['interface Vxlan1', 'default vxlan multicast-group']
        func = function('set_multicast_group', 'Vxlan1', default=True)
        self.eapi_positive_config_test(func, cmds)

    def test_set_multicast_decap(self):
        cmds = ['interface Vxlan1', 'vxlan multicast-group decap']
        func = function('set_multicast_decap', 'Vxlan1')
        self.eapi_positive_config_test(func, cmds)

    def test_set_multicast_decap_with_no_value(self):
        cmds = ['interface Vxlan1', 'no vxlan multicast-group decap']
        func = function('set_multicast_decap', 'Vxlan1', disable=True)
        self.eapi_positive_config_test(func, cmds)

    def test_set_multicast_decap_with_default(self):
        cmds = ['interface Vxlan1', 'default vxlan multicast-group decap']
        func = function('set_multicast_decap', 'Vxlan1', default=True)
        self.eapi_positive_config_test(func, cmds)

    def test_set_udp_port_with_value(self):
        cmds = ['interface Vxlan1', 'vxlan udp-port 1024']
        func = function('set_udp_port', 'Vxlan1', '1024')
        self.eapi_positive_config_test(func, cmds)

    def test_set_udp_port_with_no_value(self):
        cmds = ['interface Vxlan1', 'no vxlan udp-port']
        func = function('set_udp_port', 'Vxlan1', disable=True)
        self.eapi_positive_config_test(func, cmds)

    def test_set_udp_port_with_default(self):
        cmds = ['interface Vxlan1', 'default vxlan udp-port']
        func = function('set_udp_port', 'Vxlan1', default=True)
        self.eapi_positive_config_test(func, cmds)

    def test_update_vlan(self):
        cmds = ['interface Vxlan1', 'vxlan vlan add 10 vni 10']
        func = function('update_vlan', 'Vxlan1', 10, 10)
        self.eapi_positive_config_test(func, cmds)

    def test_remove_vlan(self):
        cmds = ['interface Vxlan1', 'vxlan vlan remove 10 vni']
        func = function('remove_vlan', 'Vxlan1', 10)
        self.eapi_positive_config_test(func, cmds)

    def test_add_vtep(self):
        cmds = ['interface Vxlan1', 'vxlan flood vtep add 1.1.1.1']
        func = function('add_vtep', 'Vxlan1', '1.1.1.1')
        self.eapi_positive_config_test(func, cmds)

    def test_add_vtep_to_vlan(self):
        cmds = ['interface Vxlan1', 'vxlan vlan 10 flood vtep add 1.1.1.1']
        func = function('add_vtep', 'Vxlan1', '1.1.1.1', vlan='10')
        self.eapi_positive_config_test(func, cmds)

    def test_remove_vtep(self):
        cmds = ['interface Vxlan1', 'vxlan flood vtep remove 1.1.1.1']
        func = function('remove_vtep', 'Vxlan1', '1.1.1.1')
        self.eapi_positive_config_test(func, cmds)

    def test_remove_vtep_from_vlan(self):
        cmds = ['interface Vxlan1', 'vxlan vlan 10 flood vtep remove 1.1.1.1']
        func = function('remove_vtep', 'Vxlan1', '1.1.1.1', vlan='10')
        self.eapi_positive_config_test(func, cmds)


if __name__ == '__main__':
    unittest.main()
